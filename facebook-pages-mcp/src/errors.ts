export class McpAppError extends Error {
  constructor(
    message: string,
    readonly code: string,
  ) {
    super(message);
    this.name = new.target.name;
  }
}

export class ConfigurationError extends McpAppError {
  constructor(message: string) {
    super(message, 'CONFIGURATION_ERROR');
  }
}

export class AccessDeniedError extends McpAppError {
  constructor(message: string) {
    super(message, 'PAGE_NOT_ALLOWED');
  }
}

export class InputError extends McpAppError {
  constructor(message: string) {
    super(message, 'INVALID_INPUT');
  }
}

export class PreviewError extends McpAppError {
  constructor(message: string, code = 'PREVIEW_ERROR') {
    super(message, code);
  }
}

export class GraphApiError extends McpAppError {
  constructor(
    message: string,
    readonly httpStatus?: number,
    readonly graphCode?: number,
    readonly graphSubcode?: number,
  ) {
    super(message, 'GRAPH_API_ERROR');
  }
}

export function serializeError(error: unknown): {
  code: string;
  message: string;
  http_status?: number;
  graph_code?: number;
  graph_subcode?: number;
} {
  if (error instanceof GraphApiError) {
    return {
      code: error.code,
      message: error.message,
      ...(error.httpStatus === undefined ? {} : { http_status: error.httpStatus }),
      ...(error.graphCode === undefined ? {} : { graph_code: error.graphCode }),
      ...(error.graphSubcode === undefined ? {} : { graph_subcode: error.graphSubcode }),
    };
  }

  if (error instanceof McpAppError) {
    return { code: error.code, message: error.message };
  }

  return {
    code: 'INTERNAL_ERROR',
    message: error instanceof Error ? error.message : 'Unexpected error',
  };
}
