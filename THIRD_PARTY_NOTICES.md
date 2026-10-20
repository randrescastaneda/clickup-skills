# Attribution

This project reuses existing integrations as dependencies rather than maintaining
copies of their API clients. Original orchestration code is covered by this
repository's LICENSE. Upstream licenses remain with their authors.

| Project | Author | Use |
| --- | --- | --- |
| [clickup-cli](https://github.com/krodak/clickup-cli) | Krzysztof Rodak | Primary CLI; adapted command examples and workflow patterns |
| [clickup-mcp](https://github.com/hauptsacheNet/clickup-mcp) | Marco Pfeiffer | Optional rich-context MCP profile |
| [clickup-mcp](https://github.com/joelpt/clickup-mcp) | Joel Thornton | Optional REST MCP backend |
| [clickup-plugin](https://github.com/clickup/clickup-plugin) | ClickUp | Official MCP and plugin layout reference |

Exact reviewed commits, package versions, and notice paths are in
`upstreams.lock.json`. Original MIT license texts are retained in `third_party/`.
`third_party/krodak/REFERENCE.md` is the upstream command reference retained for
maintainers, not another automatically loaded skill. All other workflow skills
and Python adapters were authored for this repository.

The optional GitHub profile connects to GitHub's hosted MCP service; its server
code is not copied. CLI/MCP software licenses do not remove ClickUp plan/API
limits, GitHub access requirements, or the model provider's charges.

TaazKareem's current proprietary server is intentionally not included. No code
from repositories with an unverified license is incorporated.
