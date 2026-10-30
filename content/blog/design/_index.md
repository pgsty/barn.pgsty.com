---
title: Design Notes
linkTitle: Design
description: Architectural decisions, trade-offs, and implementation boundaries behind Barn.
weight: 20
icon: fa-solid fa-pen-ruler
blog_index: cards
blog_index_columns: 2
blog_index_toggle: true
featured_image: wash
cascade:
  featured_image: wash
  reading_time: true
  toc_taxonomies: false
---

These five essays explain the architectural trade-offs behind Barn's Linux lab workflow—from the single-deployment state model under `~/.barn` and Pigsty/Ansible inventory compatibility to in-place guest convergence, image catalog verification, and host networking on macOS and Linux.

For the native macOS Virtualization.framework subsystem (`barn mac`) introduced in Barn `0.7.0`, see [Native macOS VMs](/docs/start/macos/), the [`barn mac` Reference](/docs/reference/mac/), and the [Architecture Overview](/docs/about/design/).
