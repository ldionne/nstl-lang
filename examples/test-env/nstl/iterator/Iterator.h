#define ValueType_ CONCAT(ValueType_, NSTL_PACKAGE, _, NSTL_DEPTH)
#define Iterator_ CONCAT(Iterator_, NSTL_PACKAGE, _, NSTL_DEPTH)
#if NSTL_PACKAGE == 0
    #define ValueType_0_0 ValueType
    #define Iterator_0_0 Iterator
    #include "Iterator.contents"
    #undef ValueType_0_0
    #undef ValueType_
    #undef ValueType
    #undef Iterator_0_0
    #undef Iterator_
    #undef Iterator
#endif
#if NSTL_PACKAGE == 1
    #define ValueType_1_0 ValueType
    #define Iterator_1_0 Iterator
    #include "Iterator.contents"
    #undef ValueType_1_0
    #undef ValueType_
    #undef ValueType
    #undef Iterator_1_0
    #undef Iterator_
    #undef Iterator
#endif
#if NSTL_PACKAGE == 2
    #define ValueType_2_0 ValueType
    #define Iterator_2_0 Iterator
    #include "Iterator.contents"
    #undef ValueType_2_0
    #undef ValueType_
    #undef ValueType
    #undef Iterator_2_0
    #undef Iterator_
    #undef Iterator
#endif
#if NSTL_PACKAGE == 3
    #define ValueType_3_0 ValueType
    #define Iterator_3_0 Iterator
    #include "Iterator.contents"
    #undef ValueType_3_0
    #undef ValueType_
    #undef ValueType
    #undef Iterator_3_0
    #undef Iterator_
    #undef Iterator
#endif
#if NSTL_PACKAGE == 4
    #define ValueType_4_0 ValueType
    #define Iterator_4_0 Iterator
    #include "Iterator.contents"
    #undef ValueType_4_0
    #undef ValueType_
    #undef ValueType
    #undef Iterator_4_0
    #undef Iterator_
    #undef Iterator
#endif
