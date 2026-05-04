---
name: pull-request-template
description: Use when DEA needs to create the pull request for a pipeline from the local skill template.
---

# Skill: Pull Request Template

## Purpose
Use this skill in the final DEA Git phase after commits are ready.

## Steps

1. Read `template.md` in this folder first.
2. Fill the PR title as `feat({flujo}): pipeline {nombre del flujo}` unless the user requests a different conventional type.
3. Describe only implemented artifacts and validated results.
4. Reference the related issue with `Closes #{numero}`.
5. Keep the change-type and completed-task checklists aligned with the actual work.
6. Add reviewer notes only when they are concrete and necessary.
7. Open the pull request from the pipeline branch into `develop`.

## Template

See `template.md` in this folder.

## References

- Canonical PR template for sync reference: `.github/pull_request_template.md`
