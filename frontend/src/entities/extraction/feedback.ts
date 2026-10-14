import { api, type components, unwrap } from "@/shared/api"

export type CorrectionRequest = components["schemas"]["CorrectionRequest"]

export function saveCorrection(body: CorrectionRequest) {
  return unwrap(api.POST("/api/v1/feedback", { body }))
}

export function revokeCorrection(identifier: string, version: number) {
  return unwrap(
    api.POST("/api/v1/feedback/{identifier}/revoke", {
      params: { path: { identifier } },
      body: { version },
    }),
  )
}
