# Download the dataset
git clone https://github.com/PACE-challenge/SteinerTree-PACE-2018-instances.git
# Download the winnner of PACE Track C
git clone https://github.com/HeathcliffAC/SteinerTreeProblem.git
# Compile it
pushd SteinerTreeProblem/V4
make
popd
# Compile Mehlhorn's algorithm
g++ MehlhornSteinerTree2Apx.cpp -O2 -o MehlhornSteinerTree2Apx
