#include <iostream>
#include <queue>
#include <set>
#include <vector>
#include <cmath>

using real = float;
const real epsilon = 1e-8;

struct Point {
	real x, y;
	inline bool operator< (Point other) {
		return x < other.x || y < other.y;
	}
};

struct LineSegment {
	int original_index;
	Point p1, p2;
};

inline real dist(Point p1, Point p2) {
	return hypot(p1.x-p2.x, p1.y-p2.y);
}

int main() {
	int n;
	std::cin >> n;

	std::vector<LineSegment> lines;

	for(int i = 0; i < n; i++) {
		Point p1, p2;
		std::cin >> p1.x >> p1.y >> p2.x >> p2.y;
		if(dist(p1, p2) < epsilon)
		lines.push_back({i, p1, p2});
	}

	
}
