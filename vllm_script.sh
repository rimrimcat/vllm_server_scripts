# Variables
MODEL_PATH="/home/ubuntu/models"

# Create path if not exists
mkdir -p $MODEL_PATH

_pwd=$(pwd)

STOP=""
MODEL_NAMES=()
MODEL_PATHS=()

count_level() {
    echo "$1" | awk -F'/' '{print NF-1}'
}

secho() {
    n=$(count_level $1)
    n2=$(((n - 2) * 2))
    printf "%*s" $n2 ""
    echo "$2"
}

add_models_to_list() {
    echo "D: $1"
    if [ -d "$1" ]; then
        r1=$(realpath $1)
        secho $r1 "Got folder $1, will iterate:"
        cd $1

        for file in *; do
            if [[ $STOP == "yes" ]]; then
                STOP=""
                echo "Stop signal, will stop."
                break
            fi

            add_models_to_list $file
        done

        cd ..
    fi

    # Early stopping for safetensors
    if [[ "$1" == model*.safetensors ]]; then
        r1=$(realpath $1)
        secho $r1 "Got safetensors file $1"
        d1=$(dirname "$r1")
        d2=$(dirname "$d1")

        mdl_name="$(basename "$d2")/$(basename "$d1")"

        n=${#MODEL_NAMES[@]}
        MODEL_NAMES[$n]=$mdl_name
        MODEL_PATHS[$n]=$d1

        STOP="yes"
    fi

    # GGUF
    if [[ "$1" == *.gguf ]]; then
        r1=$(realpath $1)
        secho $r1 "Got gguf file $1"
        # MODEL_NAMES+=("$1")
        # MODEL_PATHS+=("$r1")

        n=${#MODEL_NAMES[@]}
        MODEL_NAMES[$n]=$1
        MODEL_PATHS[$n]=$r1
    fi
}

# List models
add_models_to_list $MODEL_PATH
cd $_pwd

# echo ""
# echo "Got models ${MODEL_NAMES[@]}"
# echo "Got paths ${MODEL_PATHS[@]}"

exit

serve() {
    echo ""
    echo "Select model to serve"
    select yn in "Serve" "Edit Config"; do
        case $yn in
        "Edit Config")
            echo "Should edit"
            break
            ;;
        Serve)
            echo "Should serve"
            break
            ;;
        esac
    done
}

start() {
    echo ""
    echo "Select action"
    select yn in "Serve" "Edit Config"; do
        case $yn in
        "Edit Config")
            echo "Should edit"
            break
            ;;
        Serve)
            serve
            break
            ;;
        esac
    done
}

start
