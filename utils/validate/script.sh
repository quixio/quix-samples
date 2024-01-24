#!/bin/sh

RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Temporary file to store intermediate JSON array
tmp_json="/tmp/intermediate_json.json"

# Initialize an empty array and write it to the temporary file
echo '[]' > "$tmp_json"

# Use find to get a list of JSON files
find /data -name '*library.json' | while IFS= read -r file; do
    # Combine the contents of the file with the current array in the temporary file
    jq -s '.[0] + [.[1]]' "$tmp_json" "$file" > "$tmp_json.new"
    mv "$tmp_json.new" "$tmp_json"
done

function pretty_table() {
    jq -r '(.[0]|keys_unsorted|(.,map(length*"-"))),.[]|map(.)|@tsv' | column -ts $'\t'
}

# Output the combined JSON where there are duplicate library item ids
dupes=$(cat "$tmp_json" | jq '[group_by(.libraryItemId)[] | select(length > 1)[] | {libraryItemId, name, language}]')
if [ "$(echo "$dupes" | tr -d '\"')" = "[]" ]; then
    echo "There are no duplicate library item Ids"
else
    echo -e "${RED}There are duplicate library item ids${NC}"
    echo "$dupes" | pretty_table
fi