# Versioning

Current version: **v2.1.0**.

The project uses **major.minor.patch**:

- **major** ? a large change in project scope or architecture;
- **minor** ? new features or a large content batch;
- **patch** ? fixes and small corrections.

## Release checklist

Every user-facing change must be committed together with:

1. an updated `version.js`;
2. an updated version number in the footer;
3. an updated `changelog.html` and `changelog-en.html`;
4. an updated `history.html` and `history-en.html` when the current version moves to history;
5. a regenerated `history-full.pdf` / `history-full-en.pdf` when the full-history threshold is reached.

## History limit

The public history page shows the latest **7 major versions**. The full PDF history button is muted until the project has more than 7 major versions. After that, `history.js` enables the button and links to the full PDF.

## Current history

- **v2.1.0** ? flags removed, All countries restored, ingredient cards and alternatives, versioning and bilingual legal pages.
- **v2.0.0** ? 50 Middle Eastern dishes, 5 cuisines, 50 compact PDFs, license and legal page.
- **v1.0.1** ? security policy.
- **v1.0.0** ? first release with 10 Egyptian recipes.
