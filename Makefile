# Targets live in .infra/make/, one file per area. engine.mk comes first:
# the others build on the CONTAINER_ENGINE and COMPOSE it defines.
include .infra/make/engine.mk
include .infra/make/agent.mk

.DEFAULT_GOAL := agent
