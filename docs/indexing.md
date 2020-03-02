# Indexing

CubeLang allows users to access the colors of the cube stickers. The syntax is similar to accessing the element of the list but two indices are used: a 0-based index of a row and a 0-based index of a column:
![](./diagrams/out/color_indexing.svg)

An index of any particular sticker may change depending on the orientation of the cube. Stickers on the front face follow intuitive indexing: rows are numbered from top to bottom, columns: from left to right. The left, back, and right side indices work as if the cube was rotated around the Y-axis so that this side was in front. The top and bottom sides follow the similar logic, but rotation is performed around the X-axis.

The following figure shows the indexing of the 3&times;3&times;3 cube. Indexing of the stickers on a cube of a higher dimension is similar.

![](./images/indices.svg)

