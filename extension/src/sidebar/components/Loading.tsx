import { BrandMark } from "./BrandMark"

export function Loading() {
  return (
    <div className="flex items-start gap-2.5" role="status" aria-label="VidMind is responding">
      <BrandMark compact />
      <div className="flex min-w-0 flex-1 flex-col gap-2 pt-1.5" aria-hidden="true">
        <span className="skeleton-line w-[90%]" />
        <span className="skeleton-line w-[66%]" />
        <span className="skeleton-line w-[84%]" />
      </div>
    </div>
  )
}
