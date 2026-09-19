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
# -T0 does not mean "all cores": it means as many threads as fit the memory
# limit, and since xz 5.4 that limit defaults to 25% of RAM. At -9e a worker
# needs roughly 900 MB (64 MiB dictionary, so a ~674 MiB encoder, plus block
# buffers), so the default 2,925 MiB on this 11.7 GiB machine affords only two
# of them and half the cores sit idle. -M raises the ceiling so all four run.
# Check what xz will allow with: xz --info-memory
#
# The cost is a fraction of a percent of ratio -- threaded xz compresses
# independent blocks, so more blocks means slightly less redundancy found
# across them. Against halving the wall time on a 6.5 GB image, that is noise.
%.img.xz: %.img
	@echo "==> Compressing $<..."
	@xz -T0 -M 6GiB -k -f -v -9e $<

# A convenience rule to clean up all compressed files.
.PHONY: clean
clean:
	@echo "==> Removing compressed images..."
	@rm -f $(XZ_FILES)
