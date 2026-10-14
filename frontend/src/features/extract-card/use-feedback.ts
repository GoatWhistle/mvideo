import { useMutation } from "@tanstack/react-query"
import { type CorrectionRequest, revokeCorrection, saveCorrection } from "@/entities/extraction"

type FeedbackAction =
  | { kind: "save"; body: CorrectionRequest }
  | { kind: "revoke"; id: string; version: number }

export function useFeedback(onSaved: () => void) {
  return useMutation({
    mutationFn: (action: FeedbackAction) =>
      action.kind === "save"
        ? saveCorrection(action.body)
        : revokeCorrection(action.id, action.version),
    onSuccess: onSaved,
    retry: false,
  })
}
