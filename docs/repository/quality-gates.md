# Quality Gates

This checklist is the public release bar. It turns repeated review into concrete checks.

## Repository

1. README states the boundary in operational language.
2. README names what is implemented and not implemented.
3. License is present.
4. Security policy is present.
5. Governance policy is present.
6. Contribution guide is present.
7. Code of conduct is present.
8. Trademark policy is present.
9. Public contact does not expose personal email.
10. CODEOWNERS resolves to publishable GitHub identities.

## Privacy

11. No personal email appears in tracked files.
12. No local filesystem path appears in tracked files.
13. No private company domain appears in tracked files.
14. No build artifact is staged.
15. No browser test artifact is staged.
16. No `.env` file is tracked.
17. No key, certificate, or kubeconfig is tracked.
18. No tenant data is tracked.
19. No source snapshot is tracked.
20. Commit metadata uses the project contact.

## Positioning

21. The repo avoids assistant-first language.
22. The repo avoids role-worker language.
23. The repo avoids prompt-chain positioning.
24. The repo avoids vague platform claims.
25. The repo defines a concrete category boundary.
26. The repo explains source authority.
27. The repo explains claim lifecycle.
28. The repo explains reconciliation.
29. The repo explains governance.
30. The repo explains replay.

## Contracts

31. OpenAPI is present.
32. Protobuf contracts are present.
33. JSON schemas are valid JSON.
34. SQL schema compiles as text and is reviewable.
35. Event envelope has tenant id.
36. Event envelope has schema version.
37. Event envelope has causality fields.
38. Event envelope has payload hash.
39. Workload schema has policy fields.
40. Workload schema has replayable inputs.

## Runtime

41. Confidence calculation is deterministic.
42. Confidence bands are bounded.
43. Contradictions force contradicted state.
44. Source unavailability does not erase claims.
45. Drift produces a finding.
46. Non-authoritative sources cannot confirm claims.
47. Scheduler exposes dry-run behavior.
48. Scheduler emits score components.
49. Scheduler applies resource pressure.
50. Scheduler requests approval for high-risk policy paths.

## Data Model

51. Entities are tenant-scoped.
52. Relationships are tenant-scoped.
53. Claims are tenant-scoped.
54. Evidence is tenant-scoped.
55. Workloads are tenant-scoped.
56. Memories are tenant-scoped.
57. Audit events are tenant-scoped.
58. Source systems define field authority.
59. Claims have explicit state.
60. Claims preserve temporal fields.

## Security

61. Branch protection is documented.
62. Required checks are documented.
63. Code owner review is documented.
64. Force pushes are disabled after publish.
65. Branch deletion is disabled after publish.
66. Secret scanning is enabled after publish.
67. Push protection is enabled after publish.
68. Dependency review is enabled for pull requests.
69. CodeQL is enabled.
70. Dependabot is enabled.

## Deployment

71. Docker Compose exists for local development.
72. Docker build context excludes secrets.
73. Kubernetes manifests are present.
74. Helm chart renders.
75. NetworkPolicy allows DNS.
76. Runtime pods run as non-root.
77. Runtime pods drop Linux capabilities.
78. Read-only root filesystem is enabled where practical.
79. Health probes are configured.
80. Autoscaling configuration is present.

## Observability

81. OpenTelemetry collector config is present.
82. Prometheus config is present.
83. Grafana dashboard is present.
84. Workload decisions expose score components.
85. Primitive executions carry trace id.
86. Audit events carry reason codes.
87. Replay inputs include event ids.
88. Replay inputs include policy bundle version.
89. Replay inputs include model and tool versions when used.
90. Replay excludes secret values.

## Verification

91. `scripts/verify.sh` passes.
92. Python runtime tests pass.
93. Frontend lint passes.
94. Frontend build passes.
95. Frontend audit reports no high-risk vulnerabilities.
96. Helm render passes.
97. Privacy scan passes.
98. Removed-project scan passes.
99. Git worktree is clean before release.
100. GitHub Actions pass on the published commit.
