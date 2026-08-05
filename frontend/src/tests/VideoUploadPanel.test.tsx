import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import VideoUploadPanel from "../components/VideoUploadPanel";
import * as api from "../services/apiClient";
import type { VideoPredictionResponse } from "../types";

jest.mock("../services/apiClient");
const mockedApi = api as jest.Mocked<typeof api>;

// recharts renders SVG via ResizeObserver/layout measurement, which jsdom
// doesn't support — mock it to a lightweight stand-in so we test that
// VideoUploadPanel passes it the right data, not recharts' own rendering.
jest.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  ),
  LineChart: ({ children, data }: { children: React.ReactNode; data: unknown[] }) => (
    <div data-testid="line-chart" data-points={data.length}>
      {children}
    </div>
  ),
  Line: () => <div data-testid="line" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
}));

function makeVideoFile(name = "clip.mp4", type = "video/mp4") {
  return new File(["fake video bytes"], name, { type });
}

describe("VideoUploadPanel", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders the video upload panel with a file input", () => {
    render(<VideoUploadPanel />);
    expect(screen.getByRole("heading", { name: /upload a video/i })).toBeInTheDocument();
    const input = screen.getByLabelText(/upload a video/i);
    expect(input).toHaveAttribute("type", "file");
    expect(input).toHaveAttribute("accept", "video/*");
  });

  test("shows a processing message while the request is in flight", async () => {
    let resolvePromise: (value: VideoPredictionResponse) => void;
    mockedApi.predictVideo.mockReturnValue(
      new Promise((resolve) => {
        resolvePromise = resolve;
      })
    );

    render(<VideoUploadPanel />);
    const input = screen.getByLabelText(/upload a video/i);
    await userEvent.upload(input, makeVideoFile());

    expect(
      screen.getByText(/processing video… this may take a moment/i)
    ).toBeInTheDocument();

    resolvePromise!({ timeline: [] });
    await waitFor(() =>
      expect(
        screen.queryByText(/processing video… this may take a moment/i)
      ).not.toBeInTheDocument()
    );
  });

  test("renders the timeline list and chart when predictions come back", async () => {
    mockedApi.predictVideo.mockResolvedValue({
      timeline: [
        { timestamp_sec: 0.0, emotion: "happy", confidence: 0.83 },
        { timestamp_sec: 1.0, emotion: "neutral", confidence: 0.6 },
        { timestamp_sec: 2.0, emotion: "surprise", confidence: 0.71 },
      ],
    });

    render(<VideoUploadPanel />);
    const input = screen.getByLabelText(/upload a video/i);
    await userEvent.upload(input, makeVideoFile());

    await waitFor(() =>
      expect(screen.getByText(/0\.0s — happy — 83% confidence/i)).toBeInTheDocument()
    );
    expect(screen.getByText(/1\.0s — neutral — 60% confidence/i)).toBeInTheDocument();
    expect(screen.getByText(/2\.0s — surprise — 71% confidence/i)).toBeInTheDocument();

    const chart = screen.getByTestId("line-chart");
    expect(chart).toHaveAttribute("data-points", "3");
  });

  test("shows a no-faces message when the timeline is empty", async () => {
    mockedApi.predictVideo.mockResolvedValue({ timeline: [] });

    render(<VideoUploadPanel />);
    const input = screen.getByLabelText(/upload a video/i);
    await userEvent.upload(input, makeVideoFile());

    await waitFor(() =>
      expect(screen.getByText(/no faces were detected in this video/i)).toBeInTheDocument()
    );
    expect(screen.queryByTestId("line-chart")).not.toBeInTheDocument();
  });

  test("shows a session-expired message on 401", async () => {
    mockedApi.predictVideo.mockRejectedValue({ response: { status: 401 } });

    render(<VideoUploadPanel />);
    const input = screen.getByLabelText(/upload a video/i);
    await userEvent.upload(input, makeVideoFile());

    await waitFor(() =>
      expect(
        screen.getByText(/your session expired — please log in again/i)
      ).toBeInTheDocument()
    );
  });

  test("shows a generic error message on other failures", async () => {
    mockedApi.predictVideo.mockRejectedValue(new Error("network down"));

    render(<VideoUploadPanel />);
    const input = screen.getByLabelText(/upload a video/i);
    await userEvent.upload(input, makeVideoFile());

    await waitFor(() =>
      expect(
        screen.getByText(/something went wrong analyzing this video/i)
      ).toBeInTheDocument()
    );
  });
});