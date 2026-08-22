# Integrated runner stock-headless boot report

- Result: `pass`
- Coordinate: `integrated_runner_post_hmr_pre_request_hold`
- Candidate: `d36c5423e5c33c61cc9892ce9d580fbcaf850381`
- Native process count: `1`
- HMR mutation count: `1`
- Readiness: `sentinel_activated, stock_headless_hmr_ready`
- Control load: `integrated_edit_controls_loaded`
- Runner terminal: `failed` at `roots`
- Model/provider requests: `0` / `0`
- Network attempts: `0`
- Cleanup: process absent `true`, root absent `true`

The exact accepted integrated runner and its typed edit controls loaded through
one real rc.7 stock-headless HMR mutation. The deliberately single-root preset
roster stopped the runner at its closed `roots` stage before agent creation or
any worker, model, provider, broker, session, turn, tool or network request.
