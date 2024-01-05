#!/bin/sh

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

# Output the combined JSON where
cat "$tmp_json" |  jq '[.[] | {name, language, libraryItemId, shortDescription}] | sort_by(.name)' | pretty_table
