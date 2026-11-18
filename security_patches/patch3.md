# Patch 3: External binary configuration search

- **Affected component:** External-tool configuration discovery in
  `src/external_binaries.py`.
- **Affected versions:** v1.0.8 and earlier releases that include the
  external-binary configuration resolver. The fix is in the unreleased
  development line after v1.0.8.
- **Root cause:** Configuration discovery included a candidate under the
  process working directory. A manipulated working directory could therefore
  influence which configuration file was loaded for external-tool resolution.
- **Remediation:** The working-directory configuration candidate was removed.
  The explicit `FCP_EXTERNAL_BINARIES_CONF` override, frozen-application
  configuration paths, and `SRC_DIR/config/external_binaries.conf` remain
  supported. Resolution priority is unchanged: PATH, app-local directory,
  common system directories, then the configured file.
- **Verification:** Focused regression tests cover working-directory rejection,
  legitimate `SRC_DIR` configuration, and the explicit override. The focused
  suite passed 25 tests; the full suite passed 1085 tests with 8 skipped.
- **Limitations:** This patch closes only the working-directory configuration
  vector. Local PATH/app-local binary planting and the lack of executable
  identity, signature, ownership, or permission verification remain separate
  hardening concerns. Explicitly configured tools remain trusted user input.
