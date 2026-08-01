import { render, screen } from "@testing-library/react";
import UploadPanel from "../components/UploadPanel";

test("renders the upload panel with a file input", () => {
  render(<UploadPanel />);
  expect(screen.getByRole("heading", { name: /upload an image/i })).toBeInTheDocument();
  expect(screen.getByLabelText(/upload an image/i)).toHaveAttribute("type", "file");
});