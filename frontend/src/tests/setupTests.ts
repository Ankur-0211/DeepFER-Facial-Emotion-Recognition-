import { TextEncoder, TextDecoder } from "util";

// jsdom doesn't provide these globals; react-router-dom's deps need them.
globalThis.TextEncoder = TextEncoder as unknown as typeof globalThis.TextEncoder;
globalThis.TextDecoder = TextDecoder as unknown as typeof globalThis.TextDecoder;

import "@testing-library/jest-dom";