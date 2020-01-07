"""Polyline intersection solver

"""
def line_intersection(line1, line2):
    dx = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    dy = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(dx, dy)
    if div == 0:
        # TODO: special case for segment intersection
        return None

    d = (det(*line1), det(*line2))
    x = det(d, dx) / div
    y = det(d, dy) / div

    def is_inside(point,line):
        x0 = min(line[0][0],line[1][0])
        x1 = max(line[0][0],line[1][0])
        y0 = min(line[0][1],line[1][1])
        y1 = max(line[0][1],line[1][1])
        # print((x0,x1),(y0,y1))
        yes = (x0 <= point[0] and point[0] <= x1 and y0 <= point[1] and point[1] <= y1)
        # print(f"is_inside(point={point},line={line}) -> {yes}")
        return yes

    if is_inside((x,y),line1) and is_inside((x,y),line2):
        return (x,y)
    else:
        return None

def intersection(poly1, poly2):

    result = [];
    for i, A in enumerate(poly1[:-1]):
        B = poly1[i + 1]

        for j, C in enumerate(poly2[:-1]):
            D = poly2[j + 1]

            E = line_intersection((A, B), (C, D))
            if E:
                result.append(E)
    return result

if __name__ == '__main__':
    # unit test
    assert(intersection([(-1,-1),(1,1)],[(-1,1),(1,-1)]) == [(0,0)])
    assert(intersection([(-2,-2),(1,1)],[(-1,-1),(2,2)]) == [])
    assert(intersection([(-1,-1),(-1,1)],[(0,0),(1,1)]) == [])
    assert(intersection([(-1,-1),(1,-1),(1,2)],[(0,1),(2,1),(3,2)]) == [(1.0,1.0)])
