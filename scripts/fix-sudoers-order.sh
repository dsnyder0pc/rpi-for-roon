#!/bin/bash
# Description: Corrects rule precedence in /etc/sudoers so that the drop-in
#              directory is consulted after the general audiolinux rule rather
#              than before it. A default Arch sudoers puts @includedir first,
#              which lets the general rule override the specific NOPASSWD
#              exceptions in /etc/sudoers.d and makes commands that should be
#              passwordless ask for a password.
#
#              Idempotent: a file already in the right order is left untouched,
#              and a rewritten file is installed only after visudo accepts it.

set -u

SUDOERS_FILE="/etc/sudoers"

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: This script must be run as root (pipe it to 'sudo bash')." >&2
    exit 1
fi

# Already correct is the common case, and rewriting a file that does not need
# it is the one way this script could do harm. Ask first, in the same terms the
# QA check asks: the general rule must appear before the drop-in directory.
if awk '/^audiolinux ALL=\(ALL\) ALL$/ {u=NR} /^@includedir/ {i=NR} END {exit !(u && i && u < i)}' \
       "$SUDOERS_FILE"; then
    echo "Sudoers rule order is already correct. No changes made."
    exit 0
fi

TEMP_SUDOERS=$(mktemp)
trap 'rm -f "$TEMP_SUDOERS"' EXIT

# Move the drop-in include below the general audiolinux rule, preserving every
# other line and the blank line that separated them.
perl -e '
while (<>) {
  if (m{/etc/sudoers.d} and not $found_audiolinux_all) {
    pop @lines if $#lines > -1 and $lines[$#lines] =~ /^$/;
    push @drop_in, $_;
  } else {
    push @lines, $_;
  }
  if (/^audiolinux ALL=\(ALL\) ALL$/) {
    $found_audiolinux_all++;
    push @lines, ("\n", @drop_in) if @drop_in;
  }
}
print @lines;
' < "$SUDOERS_FILE" > "$TEMP_SUDOERS"

# A sudoers file that does not parse locks every user out of root, so nothing
# is installed until visudo has accepted the rewritten copy.
if [ -s "$TEMP_SUDOERS" ] && visudo -c -f "$TEMP_SUDOERS"; then
    echo "Sudoers file passed validation. Installing corrected version..."
    install -m 0440 -o root -g root "$TEMP_SUDOERS" "$SUDOERS_FILE"
    echo "Sudoers rule order corrected."
else
    echo "ERROR: The modified sudoers file failed validation. No changes were made." >&2
    exit 1
fi
