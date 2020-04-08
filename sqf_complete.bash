#!/usr/bin/env bash

function _sqf_()
{
    COMPREPLY=($(sqf complete-bash "$COMP_LINE"))
}

complete -F _sqf_ sqf
