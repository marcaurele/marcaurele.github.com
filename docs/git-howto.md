# GIT HOW-TO

## To reset a commit and come back to previous state

If you want to commit on top of the current HEAD with the exact state at a different commit, undoing all the intermediate commits, then you can use reset to create the correct state of the index to make the commit.

	# reset the index to the desired tree
	git reset 56e05fced

	# move the branch pointer back to the previous HEAD
	git reset --soft HEAD@{1}

	git commit -m "Revert to 56e05fced"

	# Update working copy to reflect the new commit
	git reset --hard
---
## A couple of useful commands

	# To create a new annotated tag
	git tag -a 0.x.x -m "my comment"
	
	# To push the tags to the master because it's not done automatically
	git push --tags