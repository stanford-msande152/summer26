---
layout: page
title: Lecture Schedule
description: Lectures, sections, readings, and homework dates.
nav_order: 2
---

# Lecture Schedule

**Lectures** (Prof. Agosta): Mon/Wed, 10:30 AM–12:30 PM, Y2E2 111 · **Discussion section:** Thu, 3:00–4:15 PM, Y2E2 111

Lecture notes are posted after each session. Readings refer to FODA (Howard & Abbas, *Foundations of Decision Analysis*) and the RH draft manuscript on Canvas.

**LECTURE**{: .label .label-green } **SECTION**{: .label .label-blue } **HW OUT**{: .label .label-yellow } **HW DUE**{: .label .label-red } **EXAM / PROJECT**{: .label .label-purple }

{% for module in site.modules %}
{{ module }}
{% endfor %}
