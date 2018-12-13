# DeEvA

This is a platform for the procedural generation of characters from personality traits.

It currently consists of several, inter-dependent, projects.

## Projects

* Character Generation: Consists of a set of scripts to procedurally generate virtual characters. It also allows for the generation of pictures of them. It uses the [ManuelBastioniLAB](http://www.manuelbastioni.com/) add-on.

* Voting Platform: Is a web-based platform (using [DJango](https://www.djangoproject.com/)) conceived to run psychological experiments where users vote on the pictures of virtual characters. The collected data is used as input for the Character Generator.

  ![Rate Voting Page](VotingPlatform/Docs/Pics/SampleExperiment-RateVotePage.png)

* MBLab-FalseTimePatch: It is a patch for the ManuelBastioniLAB allowing for the generation of characters via scripting. It is used by the CharacterGeneration project.
