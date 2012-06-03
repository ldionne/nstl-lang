#define FuncName_ CONCAT(FuncName_, NSTL_PACKAGE, _, NSTL_DEPTH)
#if NSTL_PACKAGE == 0
    #define FuncName_0_0(func) FuncName
    #include "advance.contents"
    #undef FuncName_0_0
    #undef FuncName_
    #undef FuncName
#endif
#if NSTL_PACKAGE == 1
    #define FuncName_1_0(func) FuncName
    #include "advance.contents"
    #undef FuncName_1_0
    #undef FuncName_
    #undef FuncName
#endif
#if NSTL_PACKAGE == 2
    #define FuncName_2_0(func) FuncName
    #include "advance.contents"
    #undef FuncName_2_0
    #undef FuncName_
    #undef FuncName
#endif
#if NSTL_PACKAGE == 3
    #define FuncName_3_0(func) FuncName
    #include "advance.contents"
    #undef FuncName_3_0
    #undef FuncName_
    #undef FuncName
#endif
#if NSTL_PACKAGE == 4
    #define FuncName_4_0(func) FuncName
    #include "advance.contents"
    #undef FuncName_4_0
    #undef FuncName_
    #undef FuncName
#endif
