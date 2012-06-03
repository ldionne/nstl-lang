#define FuncName_ CONCAT(FuncName_, NSTL_PACKAGE, _, NSTL_DEPTH)
#define Container_ CONCAT(Container_, NSTL_PACKAGE, _, NSTL_DEPTH)
#if NSTL_PACKAGE == 0
    #define FuncName_0_0(func) FuncName
    #define Container_0_0 Container
    #include "rbegin.contents"
    #undef FuncName_0_0
    #undef FuncName_
    #undef FuncName
    #undef Container_0_0
    #undef Container_
    #undef Container
#endif
#if NSTL_PACKAGE == 1
    #define FuncName_1_0(func) FuncName
    #define Container_1_0 Container
    #include "rbegin.contents"
    #undef FuncName_1_0
    #undef FuncName_
    #undef FuncName
    #undef Container_1_0
    #undef Container_
    #undef Container
#endif
#if NSTL_PACKAGE == 2
    #define FuncName_2_0(func) FuncName
    #define Container_2_0 Container
    #include "rbegin.contents"
    #undef FuncName_2_0
    #undef FuncName_
    #undef FuncName
    #undef Container_2_0
    #undef Container_
    #undef Container
#endif
#if NSTL_PACKAGE == 3
    #define FuncName_3_0(func) FuncName
    #define Container_3_0 Container
    #include "rbegin.contents"
    #undef FuncName_3_0
    #undef FuncName_
    #undef FuncName
    #undef Container_3_0
    #undef Container_
    #undef Container
#endif
#if NSTL_PACKAGE == 4
    #define FuncName_4_0(func) FuncName
    #define Container_4_0 Container
    #include "rbegin.contents"
    #undef FuncName_4_0
    #undef FuncName_
    #undef FuncName
    #undef Container_4_0
    #undef Container_
    #undef Container
#endif
