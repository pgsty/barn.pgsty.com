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

These essays explain Barn's state model, guest convergence, image trust, host networking, [CLI contracts](cli-contracts/), and [native Mac lifecycle](native-mac-lifecycle/). Design proposals also examine the Pigsty/Vagrant development loop, Windows hosting, and future guest architectures; each proposal states its implementation and validation status.

The native macOS Virtualization.framework subsystem (`barn mac`) was introduced in Barn `0.9.0`; its signed app has shipped in Apple Silicon archives since `0.9.2`. See [Native macOS VMs](/docs/start/macos/), the [`barn mac` Reference](/docs/reference/mac/), and the [Mac release handbook](/docs/about/mac-release/).
