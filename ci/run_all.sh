#!/usr/bin/env bash
# Run every CI guard in sequence. Exit non-zero on the first failure.
set -u

cd "$(dirname "$0")/.."

guards=(
  "ci/check_classic_degradation.py"
  "ci/check_image_budget.py"
  "ci/check_alt_text_presence.py"
  "ci/check_dead_links.py"
  "ci/check_sandbox_below_fold.py"
  "ci/check_uncategorized_empty.py"
  "ci/check_genre_coverage.py"
  "ci/check_dating_monotone_buffer.py"
  "ci/check_wxr_schema.py"
)

failed=0
for g in "${guards[@]}"; do
  echo ""
  echo "::group::$g"
  if ! python3 "$g"; then
    failed=$((failed + 1))
  fi
  echo "::endgroup::"
done

echo ""
if [ "$failed" -eq 0 ]; then
  echo "all CI guards passed"
  exit 0
fi
echo "$failed CI guard(s) failed"
exit 1
