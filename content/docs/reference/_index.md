---
title: Reference
linkTitle: Reference
description: Barn 0.9.1 configuration, command options, output formats, and image repositories.
weight: 20
icon: fa-solid fa-book-open
cascade:
  type: docs
---

Use these pages to find a field, flag, or result in **Barn 0.9.1**.
For step-by-step instructions, start with the [guides](../start/).

| Reference | Contents |
|---|---|
| [Linux configuration](configuration/) | inventory discovery, variables, defaults, disks, shares, and changes |
| [CLI](cli/) | Common options, Linux commands, structured results, and exit codes |
| [Mac commands](mac/) | macOS VM commands, settings, JSON results, and files |
| [Linux images](images/) | Image versions, repositories, signatures, imports, and cache management |
| [Image pipeline](image-pipeline/) | Contributor tools for preparing and checking Linux images |

For another version, check `barn version` and `barn <command> --help`.
The supported interface is the command line. Go packages under `internal/` are implementation details.

The image table describes the image catalog embedded in that release.
`barn update` can activate newer repository metadata without updating the executable.
Pipeline instructions cover contributor tools in the source checkout.
See [release engineering](../about/engineering/) for build and publication requirements.
