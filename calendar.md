---
layout: page
title: Lecture Schedule
description: Lectures organized by topic, with slides, readings, and problem set dates.
nav_order: 2
---

# Lecture Schedule

Lectures are Mon/Wed. Slides and notes are posted after each lecture. Readings refer to Howard & Abbas, *Foundations of Decision Analysis* unless noted.

{% for module in site.modules %}
{{ module }}
{% endfor %}
