import argparse

"""
Counts for users who watched n thru 1 videos are stored in a list with n
elements. The first element in the list corresponds to the number of people who
watched all n videos, the last element in the list are the number of people who
only saw 1 video.
"""

class VideoCounts(object):

    def __init__(self, videos):
        self.videos = videos
        self._found_users= {}
        self.num_vids = len(videos)
        self._video_counts = [0]*self.num_vids

    def add_vid_to_user(self, video, user):
        # return Num videos user has seen when adding video to user, False if video
        # already present.

        # add video to user video
        if video not in self._found_users[user]:
            self._found_users[user].append(video)
            # Returning number of videos the user has seen
            return len(self._found_users[user])

        # Video already seen by user, return False so we don't count this view
        # later.
        return False

    def read_input(self, file_name):

        with open(file_name, 'r') as f:
            for line in f:
                # TODO: figure out what indexes user and video are on line.
                parts = line.split(",")

                # Only record views for specified videos
                if parts[0] in self.videos:
                    # Pass video and user
                    self.add_vid_to_user(parts[0], parts[1])

        # Hash with users and videos they watched has been populated. Loop thru
        # it and add counts to _video_counts data structure.
        for videos in self._found_users.itervalues():
            self.add_video(len(videos))

    def add_video(vid_num):
        """
        vid_num Int number of video count column to add view to.

        # inverts the video index and makes zero indexed
        self.num_vids - vid_num
        """

        i = (self.num_vids - video_num)

        while i < self.num_vids:
            self._video_counts[i] += 1
            i += i & -i

    def sum_vid_plays(num_vid):
        total = 0
        # Invert video index and make zero indexed.
        i = self.num_vids - num_vid

        while i > 0:
            total += self._video_counts[i]
            i -= i & -i

        return total

    def access_vid_plays(num_vid):
        """
        This can be used to find the number of users who saw only n views.
        """

        i = self.num_vids - num_vid
        total = self._video_counts[i]

        if i > 0:
            z = i - (i & -i)
            i -= 1
            while i != z:
                total -= self.video_counts[i]
                i -= (i & -i)

        return total

def do_sums(videos, filepath):
    """
    videos List of video IDs.
    """

    vc = VideoCounts(videos)

    # Populate _video_counts data structure
    vc.read_input(filepath)

    print "The number of users who watched at least the number of videos:"

    for i in range(vc.num_vids):
        print "{0} video: {1} users".format(i, vc.sum_vid_plays(i))

    print "Number of users who watched exactly the number of videos:"

    for i in range(vc.num_vids):
        print "{0} video: {1} users".format(i, vc.access_vid_plays(i))


if __name__ == "__main__":

    # Get user input
    parser = argparse.ArgumentParser(
        description="Pass a list of video IDs to count the number of users who"\
            "watched a sequence of them.")

    parser.add_argument("videos", type=int, nargs="+",
        help="Space seperated list of video IDs.")
    parser.add_argument("-f", required=True, dest="filepath",
        help="Path to log file.")

    args = parser.parse_args()

    do_sums(videos, filepath)
    print args.videos
    print args.filepath


"""
This tree represents the indexes for 15 videos [1-15]


                   1000
              /            \
        0100                  1100
      /     \              /        \
   0010      0110        1011       1110
   /  \       /  \       / \        /   \
0001  0011 0101 0111  1001 1010  1101   1111

"""


