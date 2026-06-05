# Placeholder terraform file to prove the marker's defaults win even
# when an infra signal is present in the tree. The skill must not
# fall through to repo-shape heuristics when the marker resolves.
resource "null_resource" "placeholder" {}
