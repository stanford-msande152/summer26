---
layout: page
title: Lecture Schedule
description: Lectures, sections, readings, and homework dates.
nav_order: 2
---

# Lecture Schedule

**Lectures** (Prof. Agosta): Mon/Wed, 10:30 AM–12:30 PM, Y2E2 111

**Discussion section**: Thu, 3:00–4:15 PM, Y2E2 111

Readings refer to the [Howard manuscript](https://github.com/stanford-msande152/summer26/blob/main/lit/manuscript/Howard_manuscript.md) and the [References & Readings](/summer26/lit/bibliography/) page.

**LECTURE**{: .label .label-green } **SECTION**{: .label .label-blue } **HW OUT**{: .label .label-yellow } **HW DUE**{: .label .label-red } **EXAM / PROJECT**{: .label .label-purple }

📚 Full reading list, videos, and bibliography: [References & Readings](/summer26/lit/bibliography/)

{% for module in site.modules %}
{{ module }}
{% endfor %}
