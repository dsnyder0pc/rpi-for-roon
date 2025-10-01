# Find all .img files starting with "diretta-"
IMG_FILES := $(wildcard diretta-*.img)

# Create a list of the target .xz files based on the .img files
XZ_FILES := $(IMG_FILES:.img=.img.xz)

# The default goal 'all' will build all necessary .xz files.
# .PHONY means 'all' is a command, not a file.
.PHONY: all
all: $(XZ_FILES)

# This is the pattern rule. It tells 'make' how to create a .img.xz
# file from a .img file. It will only run if the .img file is newer
# than its corresponding .img.xz file, or if the .xz file doesn't exist.
%.img.xz: %.img
	@echo "==> Compressing $<..."
	@xz -T0 -k -f -v -6 $<

# A convenience rule to clean up all compressed files.
.PHONY: clean
clean:
	@echo "==> Removing compressed images..."
	@rm -f $(XZ_FILES)
