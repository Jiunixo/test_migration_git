/**
 * @file test_cgal_bridge.cpp
 *
 * @brief Test the bridge between TY* and CGAL functionalities
 *
 * @author Anthony Truchet <anthony.truchet@logilab.fr>
 *
 */


#include <vector>
#include <deque>
#include <memory>

using std::vector;
using std::deque;

#include "gtest/gtest.h"

#include "Tympan/models/common/3d.h"
#include "Tympan/models/common/plan.h"
#include "Tympan/models/common/triangle.h"
#include "Tympan/models/business/geometry/TYPolygon.h"
#include "Tympan/models/business/cgal_bridge.h"
#include "Tympan/models/business/exceptions.h"

using tympan::ITYPolygonTriangulator;

/**
 * \brief Fixture which provides a Polygon to be triangulated
*/
class TriangulatePolygonTest :
    public testing::Test
{
private:
    TYPolygon poly;

protected:
    deque<OPoint3D> points;
    deque<OTriangle> triangles;

    std::unique_ptr<ITYPolygonTriangulator> p_triangulator;

    void triangulate(const vector<TYPoint>& pts)
    {
        poly.setPoints(pts);
        p_triangulator = tympan::make_polygon_triangulator(poly);
        p_triangulator->exportMesh(points, triangles);
    }
}; // class TriangulatePolygonTest


TEST_F(TriangulatePolygonTest, single_triangle)
{
    // NB New c++'11 initializer-list syntax
    // Cf. http://en.wikipedia.org/wiki/C++11#Initializer_lists
    vector<TYPoint> pts;
    pts.push_back(TYPoint(0,0,0));
    pts.push_back(TYPoint(0,1,0));
    pts.push_back(TYPoint(1,0,0));

    triangulate(pts);

    ASSERT_EQ(3, points.size());
    ASSERT_EQ(1, triangles.size());
}


TEST_F(TriangulatePolygonTest, concave_quadrangle)
{
    vector<TYPoint> pts;
    pts.push_back(TYPoint(0,0,0));
    pts.push_back(TYPoint(5, 0,0));
    pts.push_back(TYPoint(1, 1, 0));
    pts.push_back(TYPoint(0.5, 6, 0));

    triangulate(pts);

    ASSERT_EQ(4, points.size());
    ASSERT_EQ(2, triangles.size());
}

TEST_F(TriangulatePolygonTest, vertical_face)
{
    vector<TYPoint> pts;
    pts.push_back(TYPoint(0, 0, 0));
    pts.push_back(TYPoint(1, 0, 0));
    pts.push_back(TYPoint(1, 0, 2));
    pts.push_back(TYPoint(0, 0, 2));

    triangulate(pts);

    ASSERT_EQ(4, points.size());
    ASSERT_EQ(2, triangles.size());
}

TEST_F(TriangulatePolygonTest, non_simple_face)
{
    // see https://extranet.logilab.fr/ticket/1650297
    vector<TYPoint> pts;
    pts.push_back(TYPoint(0, 0, 0));
    pts.push_back(TYPoint(2, 0, 0));
    pts.push_back(TYPoint(1, 0, 0));

    ASSERT_THROW(triangulate(pts), tympan::invalid_data);
}

