#!/usr/bin/env bash
declare DIR="$(cd "$(dirname "$0")/../addon" && pwd -P)"
declare addon_name="MigakuKanjiAddon"
declare customdir=''

if [[ -d "$customdir" ]]; then
  declare target="$customdir/$addon_name"

elif [[ -d "$HOME/.local/share/AnkiDev/addons21" ]]; then
  declare target="$HOME/.local/share/AnkiDev/addons21/$addon_name"

elif [[ $(uname) = 'Darwin' ]]; then
  declare target="$HOME/Library/Application Support/Anki2/addons21/$addon_name"

elif [[ $(uname) = 'Linux' ]]; then
  declare target="$HOME/.local/share/Anki2/addons21/$addon_name"

else
  echo 'Unknown platform'
  exit -1
fi

if [[ "$1" =~ ^-?d$ ]]; then
  if [[ ! -h "$target" ]]; then
    echo 'Directory was not linked'
  else
    rm "$target"
  fi

elif [[ "$1" =~ ^-?c$ ]]; then
  if [[ ! -h "$target" ]]; then
    ln -s "$DIR" "$target"
  else
    echo 'Directory was already linked.'
  fi

else
  echo 'Unknown command'
  exit -2
fi
