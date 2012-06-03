/* Example of a template file created by nstl. */


/* The uniqueness counter is managed individually by each template. */
{% increment the uniqueness counter %}


/* Signalization of the existence of this template. This is our mechanism for
 *	avoiding multiple includes of the same template. It is the responsibility
 *	of the caller not to instantiate the template in case it would cause
 *	duplication or conflicts.
 */
{% for depth in range(n) %}
	#if DEPTH == {% depth %}
		#define included_ ## this_temlate_at ## {% depth %} ## _h true
	#endif
{% endfor %}


/* Initialize template parameters with their default unless specified, and 
 *	make sure all the parameters are present. The instantiation fails if
 *	parameters are missing after this step.
 */
{% for i in range(n) %}
	#if I == {% i %}
		{% define all parameters with default values
		(make sure not to overwrite the specified arg if one is specified) %}
		
		{% assert all parameters without default argument are specified %}
	#endif
{% endfor %}


////////////////////////actual definition of the template/////////////////////

/* If templates are imported in order for this one to work, it is done here.
 *	This is not like a nested template in the sense that an imported
 *	template is considered to be part of this template, and for that reason the
 *	depth counter is not incremented. Nothing is done if the template was
 *	already instantiated in order to avoid bloat/multiple definition of
 *	functions.
 */
#if ! included_ ## {% the_required_template %} ## macro_expanding_to_depth()
	#include <imported/template/path.h>
#endif


/* This shows a regular function call */
{% for i in range(n) %}
	#if I == {% i %}
		{% define all the specified parameters %}
	#endif
{% endfor %}
/* Here we explicitly change the depth, which is different from an import */
{% Increment the depth counter %}
#include <nested/template/path.h>
{% Decrement the depth counter %}

//////////////////////end actual definition of the template///////////////////

/* Clean up of the template parameters at the very end */
{% for i in range(n) %}
	#if I == {% i %}
		{% undefine all parameters %}
		{% assert all parameters of the template undefined (optional) %}
	#endif
{% endfor %}

------------------------------ old specification ------------------------------



	//global definition of FuncName, in another file
#define FuncName(func) FuncName_##depth(func)

	//example use of nested templates


/* -!- cpp.autogen -!- */
	//Note : ça serait vraiment epic de permettre une fonction genre
	//			cpp.inputFrom(coordonnées ou tag quelconque que cpp va chercher
	//			dans les sources) ou sinon juste faire
	//			cpp.Macro.from(coordonnées ou definition ou je ne sais trop)
	//En gros, le cpp doit être capable d'outputer mais aussi d'inputer des
	//objets qui représentent du code preprocesseur. Plus généralement le
	//meta-reader doit être capable d'inputer du texte à partir du fichier en
	//suivant des indications. En lui indiquant les coordonnées d'une structure
	//représentant des instructions X et en lui disant de les inputer comme du
	//code ou comme de la data, on a le contrôle pas mal complet sur le
	//preprocesseur. Je pense que ce que j'essaie de faire est similaire à ce
	//que ferait un preprocesseur pour Python. De plus, je pense que ce que
	//j'essaie de faire agit un peu comme les macros Lisp, puisque je prévois
	//de faire évaluer du code Python par l'interpréteur afin de générer du
	//code quelconque (pour l'instant, j'utiliserai mes classes cpp pour
	//générer des #ifdef, mais ce n'est pas limité à ça).

	//Ensuite, le meta-reader doit parser des fichiers, y trouver du texte
	//specialement annoté et l'exécuter comme du python. Il doit agir comme un
	//REPL, un peu comme si on redirigeait l'output de l'interpréteur Python
	//dans le fichier en question.
----------------------------------------
Resultats approximatifs du script :
----------------------------------------

/* now we need a way to define what is the FuncName going to be for the
	nested template. */
#if depth == 0
#define FuncName_0(func) some_alternate_mangle_##func
#elif depth == 1
#define FuncName_1(func) some_alternate_mangle_##func
/* etc..., for all possible nested template depths. */

#endif
/* -!- cpp.autogen -!- */



/* now we can include the subtemplate. the FuncName() macro that it's going to
	use will be the one we defined. */
#define subtemplate "subtemplate.h"
#include NEST()

/* now, I have to find something equivalent to doing this : */
#define CHAOS_PP_PARAMS (0)(0)(__FILE__)
#include CHAOS_PP_ITERATE()
/* while using conditionals all around the file (which is going to bloat way
	too much). What I need is to use both the depth and the horizontal
	iteration position to mangle names, so the same template can be reused at
	the same depth in the same file. Depth == vertical iteration |
	position == horizontal iteration. if both informations can be obtained,
	then there are max_depth x max_position possibilities for different name
	manglings. */

@begin HANDLED AUTOMATICALLY
{
/* we might want to undefine the FuncName() macro for this depth, since it
	won't be used anymore. */
#if depth == 0
#undef FuncName_0
#elif depth == 1
#undef FuncName_1
/* etc..., just like for the definition */
#endif
}
@end

/* for convenience, we can redefine the macro used by the subtemplate for
	reference in our code. it must be hardcoded */
#define FuncName_used_by_the_subtemplate(func) some_alternate_mangle_##func
static inline Container FuncName(ctor) (void)
{
	Container list;
	FuncName_used_by_the_subtemplate(basic_init)(&list);
	return list;
}
...
//undef it at all costs, and don't include any templates unless it is undefined
#undef FuncName_used_by_the_subtemplate


/* as a rule of thumb, NEVER EVER include a template while you have
	non-variable macros defined. the only macros that can be defined when you
	include a template are macros that switch their definition depending on the
	instanciation depth */

