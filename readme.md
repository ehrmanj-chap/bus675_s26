# BUS675 - Advanced Business Machine Learning

Welcome! This repo has everything you'll need for the course - lectures, labs, exercises, data, and more.

## What's in here?

- **lectures/** - Jupyter notebooks for each class
- **labs/** - Hands-on assignments (usually take two class periods plus work outside of class)
- **data/** - All the datasets we'll use
- **images/** - All the images from the lectures
- **supplemental/** - Supplemental code, specific to lectures or labs

## How this works

First, you need a GitHub account, so make one if you don't already have one. Also sign up for GitHub Education (use your student email) to get those sweet student benefits.

**Fork and Clone**: You're going to fork my repository and then clone your fork to your local computer. This gives you your own copy where you can edit lectures, take notes, and work on assignments.

**Getting Updates**: Periodically, I'll release new material. To pull in updates while keeping your edits, you'll add a second git remote called "upstream" that points to my original repo. You'll only ever pull from upstream (never push to it). I'll try my best not to change files I've already released, so merge conflicts should be rare. If they do happen, we can use VS Code to handle them.

**The key thing**: Make sure you **commit and push** your changes regularly (don't just commit locally) so I can see your progress. At minimum, commit and push at the start of every class before pulling new material from upstream.

### Initial Setup

After forking and cloning your repository, run this **one time** to add the upstream remote:

```bash
git remote add upstream https://github.com/dylanwalker/bus675_s26.git
```

### Getting New Material

When I announce new material, pull it with:

```bash
git pull upstream main
```

If you get merge conflicts, VS Code will help you resolve them - just keep your local changes when in doubt.


## What to expect

Lecture notebooks have explanations, code examples, and exercises built right in. Labs are more comprehensive and let you practice with real-world scenarios.

## Questions?

Hit me up via email or just ask in class.
