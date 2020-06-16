for f in $1/*; do
	zip=$(echo "$f" | sed "s/.*\///")
	zip -j "files/$zip.zip" "$f"
done
