import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import UploadPanel from "../components/UploadPanel";
import * as api from "../services/apiClient";
import type { PredictionResponse } from "../types";
jest.mock("../services/apiClient");
const mockedApi = api as jest.Mocked<typeof api>;

function makeImageFile(name = "photo.jpg", type = "image/jpeg") {
  return new File(["fake image bytes"], name, { type });
}

describe("UploadPanel", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders the upload panel with a file input", () => {
    render(<UploadPanel />);
    expect(screen.getByRole("heading", { name: /upload an image/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/upload an image/i)).toHaveAttribute("type", "file");
  });

  test("shows an analyzing message while the request is in flight", async () => {
    let resolvePromise: (value: PredictionResponse) => void;
    mockedApi.predictImage.mockReturnValue(
      new Promise((resolve) => {
        resolvePromise = resolve;
      })
    );

    render(<UploadPanel />);
    const input = screen.getByLabelText(/upload an image/i);
    await userEvent.upload(input, makeImageFile());

    expect(screen.getByText(/analyzing…/i)).toBeInTheDocument();

    resolvePromise!({ predictions: [], timestamp: new Date().toISOString() });
    await waitFor(() => expect(screen.queryByText(/analyzing…/i)).not.toBeInTheDocument());
  });

  test("renders predictions when the request succeeds", async () => {
    mockedApi.predictImage.mockResolvedValue({
      predictions: [
        {
          emotion: "happy",
          confidence: 0.91,
          boundingBox: { x: 10, y: 10, width: 40, height: 40 },
        },
        {
          emotion: "neutral",
          confidence: 0.55,
          boundingBox: { x: 60, y: 60, width: 30, height: 30 },
        },
      ],
      timestamp: new Date().toISOString(),
    });

    render(<UploadPanel />);
    const input = screen.getByLabelText(/upload an image/i);
    await userEvent.upload(input, makeImageFile());

    await waitFor(() =>
      expect(screen.getByText(/happy — 91% confidence/i)).toBeInTheDocument()
    );
    expect(screen.getByText(/neutral — 55% confidence/i)).toBeInTheDocument();
  });

  test("shows a session-expired message on 401", async () => {
    mockedApi.predictImage.mockRejectedValue({ response: { status: 401 } });

    render(<UploadPanel />);
    const input = screen.getByLabelText(/upload an image/i);
    await userEvent.upload(input, makeImageFile());

    await waitFor(() =>
      expect(
        screen.getByText(/your session expired — please log in again/i)
      ).toBeInTheDocument()
    );
  });

  test("shows a generic error message on other failures", async () => {
    mockedApi.predictImage.mockRejectedValue(new Error("network down"));

    render(<UploadPanel />);
    const input = screen.getByLabelText(/upload an image/i);
    await userEvent.upload(input, makeImageFile());

    await waitFor(() =>
      expect(
        screen.getByText(/something went wrong analyzing this image/i)
      ).toBeInTheDocument()
    );
  });

  test("clears previous results and errors when a new file is selected", async () => {
    mockedApi.predictImage
      .mockRejectedValueOnce({ response: { status: 401 } })
      .mockResolvedValueOnce({
        predictions: [
          { emotion: "sad", confidence: 0.7, boundingBox: { x: 0, y: 0, width: 20, height: 20 } },
        ],
        timestamp: new Date().toISOString(),
      });

    render(<UploadPanel />);
    const input = screen.getByLabelText(/upload an image/i);

    await userEvent.upload(input, makeImageFile("first.jpg"));
    await waitFor(() =>
      expect(screen.getByText(/your session expired/i)).toBeInTheDocument()
    );

    await userEvent.upload(input, makeImageFile("second.jpg"));
    await waitFor(() =>
      expect(screen.getByText(/sad — 70% confidence/i)).toBeInTheDocument()
    );
    expect(screen.queryByText(/your session expired/i)).not.toBeInTheDocument();
  });
});