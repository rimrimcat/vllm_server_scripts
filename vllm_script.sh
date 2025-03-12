#!/bin/bash

# Variables
MODEL_PATH="/home/ubuntu/models"
CONFIG_PATH="/home/ubuntu/configs"
VALID_ARGS_PATH="/home/ubuntu/vllm_server_scripts/VLLM_VALID_ARGS.txt"
# TODO: LOG PATH

# Create path if not exists
mkdir -p $MODEL_PATH
mkdir -p $CONFIG_PATH

_pwd=$(pwd)

STOP=""
MODEL_NAMES=()
MODEL_PATHS=()

# Get config path given the model name
config_of()
{
    local config_name=$(echo "$1" | sed -r 's/[\/.]+/_/g')
    local config_path="$CONFIG_PATH/$config_name"

    if [ ! -f "$config_path" ]; then
        touch "$config_path"
    fi

    echo "$config_path"
}

add_models_to_list()
{
    if [ -d "$1" ]; then
        r1=$(realpath $1)
        # secho $r1 "Got folder $1, will iterate:"
        cd $1

        for file in *; do
            if [[ $STOP == "yes" ]]; then
                STOP=""
                # echo "Stop signal, will stop."
                break
            fi

            add_models_to_list $file
        done

        cd ..
    fi

    # Early stopping for safetensors
    if [[ $1 == model*.safetensors ]]; then
        r1=$(realpath $1)
        # secho $r1 "Got safetensors file $1"
        d1=$(dirname "$r1")
        d2=$(dirname "$d1")

        mdl_name="$(basename "$d2")/$(basename "$d1")"

        n=${#MODEL_NAMES[@]}
        MODEL_NAMES[$n]=$mdl_name
        MODEL_PATHS[$n]=$d1

        STOP="yes"
    fi

    # GGUF
    if [[ $1 == *.gguf ]]; then
        r1=$(realpath $1)
        # secho $r1 "Got gguf file $1"

        n=${#MODEL_NAMES[@]}
        MODEL_NAMES[$n]=$1
        MODEL_PATHS[$n]=$r1
    fi
}

# List models
add_models_to_list $MODEL_PATH
cd $_pwd

print_models()
{
    local i
    local c
    for i in "${!MODEL_NAMES[@]}"; do
        c=$((i + 1))
        echo "$c) ${MODEL_NAMES[$i]}"
    done
}

print_config()
{
    if [ ! -s "$1" ]; then
        # Empty file
        echo "  (Defaults)"
        return
    fi

    # Contents
    while read line; do

        name=$(echo "$line" | cut -d' ' -f1)
        grep -q "$name" "$VALID_ARGS_PATH"

        if [ $? -ne 0 ]; then
            line="$line (UNKNOWN ARGUMENT!!!)"
        fi
        echo "  $line"
    done < $1
}

# config file to args
config_opts()
{
    local line
    opts=""

    while read line; do
        if [[ -z $options ]]; then
            opts="$opts --$line"
        fi
    done < "$1"
    echo "$opts"
}

###############
start()
{
    trap "exit" SIGINT
    clear

    local sel

    echo "Select action"
    select sel in "Serve" "Download"; do
        case $sel in
            Serve)
                select_model
                break
                ;;
            Download)
                echo "Not implemented yet (use dl.py instead)"
                break
                ;;
        esac
    done
}

select_model()
{
    trap "start" SIGINT
    clear

    local user_input
    local valid=false
    while ! $valid; do
        # Print models
        echo "Select model"

        print_models

        read -p "#? " user_input

        # Check if the input is a valid number and within the array bounds
        if [[ $user_input =~ ^[0-9]+$ ]] && ((user_input >= 1 && user_input <= ${#MODEL_NAMES[@]})); then
            valid=true
            SELECTED_MODEL=$((user_input - 1))
            finalize_serve
        else
            echo "Invalid input!"
            echo ""
        fi
    done

    exit
}

finalize_serve()
{
    trap "select_model" SIGINT
    clear
    local sel
    local options
    local model_name=${MODEL_NAMES[$SELECTED_MODEL]}
    local model_path=${MODEL_PATHS[$SELECTED_MODEL]}
    local config_path=$(config_of "$model_name")

    # Show config
    echo "Model: $model_name"
    echo "Settings:"
    print_config "$config_path"

    echo ""
    echo "Select action"
    select sel in "Serve" "Edit Config"; do
        case $sel in
            Serve)
                trap "exit" SIGINT
                trap "unset MODEL" EXIT

                export MODEL="$model_path"
                options=$(config_opts "$config_path")

                if [[ -z $options ]]; then
                    echo "Will use no option"
                    vllm serve "$model_path" | tee log
                else
                    echo "Will use option"
                    vllm serve "$model_path" $options | tee log
                fi

                exit
                ;;
            "Edit Config")
                vi $(config_of $model_name)
                finalize_serve
                ;;
        esac
    done
}

start
