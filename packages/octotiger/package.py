# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.error import SpackError
from spack.package import *


class Octotiger(CMakePackage, CudaPackage, ROCmPackage):
    """Octo-Tiger is an astrophysics program simulating the evolution of star
    systems based on the fast multipole method on adaptive Octrees. It was
    implemented using high-level C++ libraries, specifically HPX and Kokkos,
    which allows its scalability and usage on different hardware platforms."""

    homepage = "https://github.com/STEllAR-GROUP/octotiger"
    url = "https://github.com/STEllAR-GROUP/octotiger/archive/refs/tags/v0.8.0.zip"
    git = "https://github.com/STEllAR-GROUP/octotiger"

    maintainers("G-071")

    # Development versions
    version("develop", branch="develop", submodules=True)
    version("master", branch="master", submodules=True, preferred=True)
    # Official Github Releases
    # -> 0.10.0 New kernel fusions, SIMD and SYCL features
    version("0.10.0", sha256="1849c8e5505a2be16a55041f64e0241d9b832dabd14197cf5433ca77dbbb1f6c")
    # -> 0.9.0 Contains CUDA/HIP and Kokkos Implementation for Hydro and Gravity
    version("0.9.0", sha256="7d44f24a40a2dfb234faba57774614fe6db5b35aea657e7152ec0a008da10629")
    # -> 0.8.0 Contains new hydro solver (CPU-only)
    version("0.8.0", sha256="02a19f0f86e9a379f2615e70cb031f6527e80ca13177a3b9e5e945722d15896e")
    # Unofficial Releases - no offical github reelase but noteworthy tags/snapshots before major changes
    # -> 0.7.0 Before hydro refactoring (last tested with gcc@10)
    version("0.7.0", sha256="067add5fc747e2a695502ca33d82a654e5625d5bf1a0942183124e2d7ad269e1")
    # -> 0.6.0 Before SoA datastructure conversion and before any CUDA work (last tested with gcc@10)
    version("0.6.0", sha256="14d97a0180a0e4b3b09e16526c7e22d0682335e3430ae0309f079875b15eefd2")
    

    # Patch minor issues depending on what version/variants we are using
    # Note that all patches/fixes have been upstreamed and are only required for the old versions
    patch("add_missing_headers_for_060.patch", when="@0.6.0")
    patch("add_missing_headers_for_070.patch", when="@0.7.0")
    patch("cast_workaround_for_070cuda.patch", when="@0.7.0+cuda")
    patch("fpic_workaround_for_070cuda.patch", when="@0.7.0+cuda")
    patch("add_missing_headers_for_080.patch", when="@0.8.0")
    patch("fix_sycl_for_0100.patch", when="@0.10.0+sycl")


    # All available variants:
    variant('sycl', default=False, when="@0.10.0:",
            description=("Build octotiger with SYCL (also allows Kokkos"
                         " kernels to run with SYCL)"))
    variant('cuda', default=False, when="@0.7.0:",
            description=("Build octotiger with CUDA support"))
    variant('rocm', default=False, when="@0.9.0:",
            description=("Build octotiger with ROCm support"))
    variant('kokkos', default=False, when="@0.9.0:",
            description='Build octotiger with kokkos based kernels')
    variant('griddim', default='8', description='Octotiger grid size',
            multi=False)
    variant('theta_minimum', default='0.34', 
            description='Octotiger minimal allowed theta value',
            values=('0.5', '0.34', '0.26' , '0.16'), multi=False)
    variant('kokkos_hpx_kernels', default=False, when='@0.9.0: +kokkos ',
            description=("Use HPX execution space for CPU Kokkos kernels"
                         " (instead of the Serial space)"))
    variant('monopole_host_tasks', default='1', when='@0.10.0:', 
            description=("Tasks per monopole kernel invocation when using u"
                         " the Kokkos HPX execution space"),
            values=('1', '4', '16'), multi=False)
    variant('multipole_host_tasks', default='1', when='@0.10.0:', 
            description=("Tasks per multipole kernel invocation when using"
                         " the Kokkos HPX execution space"),
            values=('1', '4', '16', '64'), multi=False)
    variant('hydro_host_tasks', default='1', when='@0.10.0:', 
            description=("Tasks per hydro kernel invocation when using the"
                         " Kokkos HPX execution space"), multi=False)
    variant('simd_library', default='KOKKOS', when='@0.10.0: +kokkos',
            description=("Use either kokkos (for kokkos simd types) or std"
                         " (for std::experimental::simd types)"),
            values=('KOKKOS', 'STD'), multi=False)
    variant('simd_extension', default='DISCOVER', when='@0.9.0:',
            description=("Enforce specific SIMD extension or autoselect "
                         "(discover) appropriate one"),
            values=('DISCOVER', 'SCALAR', 'AVX', 'AVX512', 'NEON', 'SVE'),
            multi=False)
    variant('fast_fp_contract', default=False, when='@0.9.0:',
            description=("Enable aggressive fp-contract=fast and fmad for kernels. "
                         "Required to be False for hybrid CPU+GPU runs "))
    variant('boost_multiprecision', default=False,
            description=("Use Boost.Multiprecision Instead of GCC "
                         "Quad-Precision Math Library"))
    variant('cxx20', default=False,
            description=("Compile Octo-Tiger with c++20"))

    # Misc dependencies:
    depends_on('cmake@3.16.0:', type='build')
    depends_on('vc@1.4.1')
    depends_on('boost@1.61.0: cxxstd=14', when="@0.8.0")
    depends_on('boost@1.74.0: cxxstd=17', when="@0.9.0:")
    depends_on('hdf5 +threadsafe +szip +hl -mpi ')
    depends_on('silo@4.10.2-bsd:4.11-bsd ')
    # depends_on('silo@4.10.2 -mpi ', when='-mpi')
    depends_on('cuda', when='+cuda')
    depends_on("dpcpp", when="+sycl")

    # Pick HPX version and cxxstd depending on octotiger version:
    depends_on('hpx@:1.4.1 cxxstd=14 ', when='@:0.8.0')
    depends_on('hpx@1.6:1.7 cxxstd=17 ', when='@0.9.0')
    depends_on('hpx@1.8.0: cxxstd=17 ', when='@0.10.0:')
    # Pick HPX GPU variants depending on octotiger's GPU variants:
    depends_on('hpx +cuda +async_cuda ', when='+cuda')
    depends_on('hpx +rocm ', when='+rocm')
    depends_on('hpx -cuda -rocm', when='-cuda -rocm')
    depends_on("hpx +sycl ", when="+sycl")

    # Pick hpx-kokkos version that fits octotigers variant:
    depends_on('hpx-kokkos@0.4.0:', when='@0.10.0:+kokkos')
    depends_on('hpx-kokkos@:0.2.0', when='@0.9.0+kokkos')
    # hpx-kokkos GPU variant
    depends_on("hpx-kokkos +sycl ", when="+sycl+kokkos")
    depends_on('hpx-kokkos +cuda',
               when='+kokkos +cuda')
    depends_on('hpx-kokkos -cuda',
               when='+kokkos -cuda')

    # Pick cppuddle version that fits octotigers variant:
    depends_on('cppuddle@0.2.1: +hpx', when='@0.10.0:')
    depends_on('cppuddle@0.1.0:0.2.1 ', when='@0.9.0')

    # Pick Kokkos Version depending on Octotiger version:
    depends_on("kokkos@:3.6.01 ", when="@0.9.0+kokkos")
    depends_on("kokkos@3.6.01: ", when="@0.10.0:+kokkos")
    depends_on("kokkos@4.1.00: +hpx ",
                when="+kokkos_hpx_kernels @0.10.0:")
    depends_on("kokkos@:3.6.01 +hpx +hpx_async_dispatch ",
               when="+kokkos_hpx_kernels @0.9.0")
    # Pick Kokkos execution spaces and GPU targets depending on the octotiger targets:
    kokkos_string = 'kokkos +serial +aggressive_vectorization '
    depends_on("kokkos +sycl ", when="+sycl+kokkos")
    depends_on(kokkos_string + ' -cuda -cuda_lambda -wrapper',
               when='+kokkos -cuda')
    depends_on(kokkos_string + ' +wrapper ', when='+kokkos +cuda %gcc')
    for sm_ in CudaPackage.cuda_arch_values:
        # This loop propgates the chosem cuda_arch to kokkos.
        depends_on(kokkos_string + ' +cuda +cuda_lambda cuda_arch={0}'.format(
            sm_), when='+kokkos +cuda cuda_arch={0}'.format(sm_))
        depends_on('hpx-kokkos +cuda cuda_arch={0}'.format(sm_),
                when='+kokkos +cuda cuda_arch={0}'.format(sm_))
        depends_on('hpx +cuda cuda_arch={0}'.format(sm_),
                when='+cuda cuda_arch={0}'.format(sm_))
    for gfx in ROCmPackage.amdgpu_targets:
        # This loop propgates the chosem amdgpu_target to hpx, kokkos and hpx-kokkos.
        depends_on(kokkos_string + ' +rocm amdgpu_target={0}'.format(gfx),
                   when='+kokkos +rocm amdgpu_target={0}'.format(gfx))
        depends_on('hpx +rocm amdgpu_target={0}'.format(gfx),
                   patches=['hpx_rocblas.patch'],
                   when='+rocm amdgpu_target={0}'.format(gfx))
        depends_on('hpx-kokkos@master +rocm amdgpu_target={0}'.format(gfx),
                   when='+kokkos +rocm amdgpu_target={0}'.format(gfx))


    # Known conflicts

    # See issue https://github.com/STEllAR-GROUP/hpx/issues/5799
    conflicts("+kokkos ^kokkos@4.1.00: +cuda +hpx", when="%gcc",
              msg=("Using hpx sender/receiver backend (kokkos@4.1.0:) with nvcc does not work."
                   "Use clang or downgrade Kokkos, or deactivate +hpx"))
    conflicts("%gcc@12", when="@0.8.0",
            msg="Octotiger release 0.8.0 does not work with gcc@12 - try an older one!")
    conflicts("+cuda", when="cuda_arch=none")
    conflicts("+rocm", when="@0.8.0")
    conflicts("+kokkos_hpx_kernels", when="~kokkos")
    conflicts("simd_library=STD", when="%gcc@:10")
    conflicts("simd_library=STD", when="%clang")
    conflicts("simd_extension=SVE simd_library=STD", when="~cxx20")
    conflicts("+cuda", when="+rocm",
              msg="CUDA and ROCm are not compatible in Octo-Tiger.")
    conflicts("+cuda", when="@:0.6.0",
              msg="Octo-Tiger version too old for CUDA.")
    conflicts("+rocm", when="-kokkos",
              msg="ROCm support requires building with Kokkos for the correct arch flags.")

    build_directory = "spack-build"

    def cmake_args(self):
        spec, args = self.spec, []

        # CUDA & Kokkos config
        args.append(self.define_from_variant('OCTOTIGER_WITH_CUDA', 'cuda'))
        args.append(self.define_from_variant('OCTOTIGER_WITH_KOKKOS', 'kokkos'))
        if '+cuda' in spec:
            cuda_arch_list = spec.variants['cuda_arch'].value
            cuda_arch = cuda_arch_list[0]
            if cuda_arch != 'none':
                args.append('-DOCTOTIGER_CUDA_ARCH=sm_{0}'.format(cuda_arch))
                args.append('-DCMAKE_CUDA_ARCHITECTURES={0}'.format(cuda_arch))

        # HIP config
        args.append(self.define_from_variant('OCTOTIGER_WITH_HIP', 'rocm'))
        if "+rocm" in self.spec:
            args += [self.define("CMAKE_CXX_COMPILER", self.spec["hip"].hipcc)]
        # SYCL config
        if "+sycl ^dpcpp" in self.spec:
            args += [self.define("CMAKE_CXX_COMPILER",
                                 "{0}/bin/clang++".format(spec["dpcpp"].prefix))]

        # SIMD & CPU kernel config
        if spec.satisfies("@0.9.0"):
            if spec.satisfies("simd_extension=DISCOVER"):
                args.append('-DOCTOTIGER_WITH_FORCE_SCALAR_KOKKOS_SIMD=OFF')
            elif spec.satisfies("simd_extension=SCALAR"):
                args.append('-DOCTOTIGER_WITH_FORCE_SCALAR_KOKKOS_SIMD=ON')
            else:
                raise SpackError(("simd_extension != [DISCOVER, SCALAR] requires a newer"
                                  "Octo-Tiger version (>0.9.0)"))
        else:
            args.append(self.define_from_variant(
                'OCTOTIGER_KOKKOS_SIMD_LIBRARY', 'simd_library'))
            args.append(self.define_from_variant(
                'OCTOTIGER_KOKKOS_SIMD_EXTENSION', 'simd_extension'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_MONOPOLE_HOST_HPX_EXECUTOR', 'kokkos_hpx_kernels'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_MULTIPOLE_HOST_HPX_EXECUTOR', 'kokkos_hpx_kernels'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_HYDRO_HOST_HPX_EXECUTOR', 'kokkos_hpx_kernels'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_KOKKOS_MULTIPOLE_TASKS', 'multipole_host_tasks'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_KOKKOS_MONOPOLE_TASKS', 'monopole_host_tasks'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_KOKKOS_HYDRO_TASKS', 'hydro_host_tasks'))
        if (("~kokkos_hpx_kernels" in spec or "-kokkos_hpx_kernels" in spec) and
            spec.satisfies("@0.10.0:")):
            if int(spec.variants["multipole_host_tasks"].value) > 1:
                raise SpackError("multipole_host_tasks > 1 requires +kokkos_hpx_kernels")
            if int(spec.variants["monopole_host_tasks"].value) > 1:
                raise SpackError("monopole_host_tasks > 1 requires +kokkos_hpx_kernels")
            if int(spec.variants["hydro_host_tasks"].value) > 1:
                raise SpackError("hydro_host_tasks > 1 requires +kokkos_hpx_kernels")
        args.append(self.define('OCTOTIGER_WITH_VC', 'ON'))
        args.append(self.define('OCTOTIGER_WITH_LEGACY_VC', 'OFF'))
        # Required for SVE SIMD on A64Fx
        if spec.target == "a64fx":
            args.append(self.define('OCTOTIGER_WITH_CXX20', 'ON'))


        # Tests
        args.append(self.define('OCTOTIGER_WITH_TESTS', self.run_tests))
        if self.run_tests and not (spec.satisfies("griddim=8")
                                   or spec.satisfies("griddim=16")):
            raise SpackError("Octo-Tiger tests only work with griddim=8 and griddim=16. "
                             "Disable tests or change griddim!")
        if not self.run_tests or (spec.satisfies("%arm") or spec.satisfies("%clang") or spec.target == "neoverse_v2" or
           spec.satisfies("+rocm") or spec.satisfies("+sycl") or spec.target == "a64fx"):
            args.append(self.define('OCTOTIGER_WITH_BLAST_TEST', 'OFF'))
        else:
            args.append(self.define('OCTOTIGER_WITH_BLAST_TEST', 'ON'))

        # Compute config
        args.append(self.define_from_variant('OCTOTIGER_WITH_FAST_FP_CONTRACT', 'fast_fp_contract'))
        args.append('-DOCTOTIGER_WITH_GRIDDIM={0}'.format(spec.variants['griddim'].value))
        args.append('-DOCTOTIGER_THETA_MINIMUM={0}'.format(spec.variants['theta_minimum'].value))
        args.append(self.define('OCTOTIGER_WITH_MAX_NUMBER_FIELDS', '15'))
        if int(spec.variants["griddim"].value) > 20:
            args.append('-DOCTOTIGER_DISABLE_ILIST=ON')
        else:
            args.append('-DOCTOTIGER_DISABLE_ILIST=OFF')
        args.append(self.define('OCTOTIGER_ARCH_FLAG', '-march=native '))

        # Misc
        args.append(self.define('OCTOTIGER_WITH_UNBUFFERED_STDOUT', 'OFF'))
        args.append(self.define('CMAKE_EXPORT_COMPILE_COMMANDS', 'ON'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_BOOST_MULTIPRECISION', 'boost_multiprecision'))
        args.append(self.define_from_variant(
            'OCTOTIGER_WITH_CXX20', 'cxx20'))

        return args

    def check(self):
        if self.run_tests:
            # Redefine ctest to make sure -j parameter is dropped 
            # (No parallel tests allowed as HPX needs all cores for
            # each test)
            with working_dir(self.build_directory):
                ctest("--output-on-failure")

    # Not required due to adding setup_dependent environment in the dpcpp package
    # def setup_run_environment(self, env):
    #     if self.spec.satisfies("+sycl"):
    #         env.prepend_path("LD_LIBRARY_PATH", join_path(self.spec["dpcpp"].prefix, "lib"))

    # def setup_build_environment(self, env):
    #     if self.spec.satisfies("+sycl"):
    #         env.prepend_path("LD_LIBRARY_PATH", join_path(self.spec["dpcpp"].prefix, "lib"))
