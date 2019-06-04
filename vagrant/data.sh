main () {
  # Wait for the VM to become available
  until (echo "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'A1a2a_'" | mysql $@); do
    echo "Retrying..." 1>&2
    sleep 5
  done

  echo "Privileges granted"

  echo "CREATE DATABASE IF NOT EXISTS phenome10k" | mysql $@

  echo "Database created"
}

# A little wrapper function to strip the mysql password warning from stderr
(
  (
  (
    (
    (
      main $@
    ) 1>&9
    ) 2>&1
  ) | fgrep --line-buffered -v 'mysql: [Warning] Using a password on the command line interface can be insecure.'
  ) 1>&2
) 9>&1
