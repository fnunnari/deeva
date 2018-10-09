#!/usr/bin/env bash

# Creates / Updates the UML class diagrams


get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

#
# The directory where this script resides
DIR=`dirname "$0"`
ABS_DIR=$(get_abs_filename $DIR)
echo Running from $ABS_DIR
cd "$ABS_DIR"

echo "Activating Python environment..."
source ../p3env/bin/activate

pushd ../deeva

# PDF version
echo "Creating PDF..."
python manage.py graph_models experiments questions news | dot -Tpdf > ../Docs/VotingPlatform-ERD.pdf

# PNG version
echo "Creating PNG..."
python manage.py graph_models experiments questions news | dot -Tpng > ../Docs/VotingPlatform-ERD.png

popd

echo "Done."
