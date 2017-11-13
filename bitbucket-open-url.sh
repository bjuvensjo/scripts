clone_url="$(git remote get-url origin | sed -E "s/(.*\/\/).*@(.*)/\1\2/" )"
open "$clone_url"
