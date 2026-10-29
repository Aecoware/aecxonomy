# Contributing

Thank you for helping. The taxonomy is only useful if people in the industry agree with its words, so proposals from practice are the most valuable input.

## How a change gets in

1. **Open an issue** with the concept proposal form. Use one issue for each concept or for one small group of related concepts.
2. **A maintainer reviews it.** We check that the concept is not already in the taxonomy, that it fits one parent, and that the definition follows the writing rules below.
3. **A person decides.** AI tools help us draft and check, but a maintainer approves every change.
4. **The change goes into a release** and the CHANGELOG lists it.

Pull requests are welcome for small fixes, such as a typo or a broken link. For a new concept, open an issue first.

## Writing rules for definitions

- Write one or two sentences. Use 25 words or fewer in each sentence.
- Use the active voice and simple words. Give each word one meaning.
- Start with the type of thing: "A document that...", "A person who...", "A period in which...".
- Do not use the term in its own definition.
- Write in US English. Give the UK term when it is different.

## What we cannot accept

- **Text from closed or paid standards.** Do not copy definitions, tables, codes or titles from ISO standards, RIBA documents, MasterFormat, UniFormat, OmniClass, codes or contract forms. Write the definition in your own words. You can name the standard as a source.
- **Uniclass titles.** We link to Uniclass by code only.
- **Client, project or company data.** Do not include names, documents or details from real projects or employers.
- **Text you do not have the right to share.**

## Pull requests

- Run `python3 scripts/taxo.py check` before you open a pull request. It must pass with no errors.
- Do not change existing codes. New codes are given by a maintainer when the change is accepted.
- Keep one topic in each pull request.

## Sign your work

We use the Developer Certificate of Origin (https://developercertificate.org). Add a sign-off line to each commit with `git commit -s`. The sign-off says that you wrote the change or have the right to submit it under the licences of this repository.

## Licence of contributions

By contributing, you agree that your contribution is licensed under the same licences as this repository: CC BY 4.0 for taxonomy content and Apache License 2.0 for code.

## Conduct

Be respectful and specific. Disagree with the idea, not the person.
