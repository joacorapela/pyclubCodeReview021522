import sys
sys.path.append("../src")
import argparse
import datetime
import pandas as pd
import matplotlib.pyplot as plt

import aeon.preprocess.api as api

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', help="root directory", type=str,
                        default="../../data/")
    args = parser.parse_args(); 

    root = args.root

    plt.ion()
    data = api.sessiondata(root)
    annotations = api.annotations(root)

    data = api.sessionduration(data)                                         # compute session duration

    for session in data.itertuples():                                         # for all sessions
        if pd.isnull(session.end):
            continue
        print('{0} on {1}...'.format(session.id, session.Index))              # print progress report
        start = session.start                                                 # session start time is session index
        end = start + session.duration                                        # end time = start time + duration
        position = api.positiondata(root, start=start, end=end)              # get position data between start and end
        position = position[position.area < 2000]                             # filter for objects of the correct size

        encoder1 = api.encoderdata(root, 'Patch1', start=start, end=end)     # get encoder data for patch1 between start and end
        encoder2 = api.encoderdata(root, 'Patch2', start=start, end=end)     # get encoder data for patch2 between start and end
        pellets1 = api.pelletdata(root, 'Patch1', start=start, end=end)      # get pellet events for patch1 between start and end
        pellets2 = api.pelletdata(root, 'Patch2', start=start, end=end)      # get pellet events for patch2 between start and end

        wheel1 = api.distancetravelled(encoder1.angle)                       # compute total distance travelled on patch1 wheel
        wheel2 = api.distancetravelled(encoder2.angle)                       # compute total distance travelled on patch2 wheel
        pellets1 = pellets1[pellets1.event == 'TriggerPellet']                # get timestamps of pellets delivered at patch1
        pellets2 = pellets2[pellets2.event == 'TriggerPellet']                # get timestamps of pellets delivered at patch2

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)                    # create a figure with subplots

        ax1.plot(position.x, position.y, alpha=0.4)                           # plot position data as a path trajectory
        forage = position.reindex(pellets2.index, method='nearest')           # get position data when a pellet is delivered at patch2
        forage.plot.scatter('x','y',s=1,c='red',ax=ax1)                       # plot mouse positions when pellets were delivered
        ax1.set_xlabel('x position (pixels)')                                 # set axis label
        ax1.set_ylabel('y position (pixels)')                                 # set axis label

        for trial in pellets2.itertuples():                                   # for each pellet delivery
            before = trial.Index - pd.to_timedelta(5, 's')                    # get the previous 5 seconds
            path = position.loc[before:trial.Index]                           # get position data in the time before pellet delivery
            ax1.plot(path.x, path.y)                                          # plot path traces preceding pellet delivery

        ax2.hist(position.area, bins=100)                                     # plot histogram of tracked object size
        ax2.set_xlabel('object size (pixels^2)')                              # set axis label
        ax2.set_ylabel('count')                                               # set axis label

        wheel1.plot(ax=ax3)                                                   # plot distance travelled on patch1 wheel
        wheel2.plot(ax=ax4)                                                   # plot distance travelled on patch2 wheel
        ax3.set_ylabel('distance (cm)')                                       # set axis label
        ax4.set_ylabel('distance (cm)')                                       # set axis label

        plt.tight_layout()

        fig.set_size_inches(7.0, 7.0)
        fig.savefig('{0}_{1}.png'.format(session.id,start.date()))            # save figure tagged with id and date

        plt.show()

    import pdb; pdb.set_trace()

if __name__ == "__main__":
    main(sys.argv)
