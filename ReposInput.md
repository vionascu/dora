# DORA – Repository Inputs

This file defines all repositories to be analyzed. Only repositories listed here are processed by the system.

## TrailEquip
repo: https://github.com/vionascu/TrailEquip
branch: main
language: java
ci: github-actions
coverage: jacoco

## TrailWaze
repo: https://github.com/vionascu/TrailWaze
branch: main
language: mixed
ci: github-actions
coverage: lcov

## RnDMetrics
repo: https://github.com/vionascu/RnDMetrics
branch: main
language: python
ci: github-actions
coverage: pytest-cov
