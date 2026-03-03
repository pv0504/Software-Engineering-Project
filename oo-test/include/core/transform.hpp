#pragma once


namespace ootest { namespace core {


    struct Transform {
        double x{0}, y{0}, z{0};
        Transform() = default;
        Transform(double X, double Y, double Z): x(X), y(Y), z(Z) {}
        double magnitude() const;
        struct Helper { 
            static double sq(double v) { return v*v; }
        };
    };


} }
