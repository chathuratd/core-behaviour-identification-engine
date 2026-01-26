// src/components/LandingPage.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform, useInView } from 'framer-motion';
import {
  ShieldCheck,
  ArrowRight,
  BrainCircuit,
  Lock,
  Sparkles,
  Database,
  Wifi,
  Users,
  Globe,
  Zap,
  ChevronRight,
  ExternalLink,
} from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/signin');
  };

  const { scrollYProgress } = useScroll();
  const heroOpacity = useTransform(scrollYProgress, [0, 0.5], [1, 0.6]);
  const heroScale = useTransform(scrollYProgress, [0, 0.5], [1, 1.15]);

  const FadeInSection = ({ children, delay = 0 }) => {
    const ref = React.useRef(null);
    const isInView = useInView(ref, { 
      once: false,
      margin: "-100px" 
    });

    return (
      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 60 }}
        animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 60 }}
        transition={{ duration: 0.8, delay, ease: "easeOut" }}
      >
        {children}
      </motion.div>
    );
  };

  const StaggerContainer = ({ children }) => {
    const ref = React.useRef(null);
    const isInView = useInView(ref, { 
      once: false,
      margin: "-100px" 
    });

    return (
      <motion.div
        ref={ref}
        variants={{
          hidden: { opacity: 0 },
          show: {
            opacity: 1,
            transition: { staggerChildren: 0.15 }
          }
        }}
        initial="hidden"
        animate={isInView ? "show" : "hidden"}
      >
        {children}
      </motion.div>
    );
  };

  const StaggerItem = ({ children }) => (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 40 },
        show: { opacity: 1, y: 0, transition: { duration: 0.6 } }
      }}
    >
      {children}
    </motion.div>
  );

  const AnimatedButton = ({ children, onClick, variant = "primary", className = "" }) => {
    const baseClasses = "relative overflow-hidden rounded-2xl font-black flex items-center justify-center gap-3 transition-all duration-300";

    const variants = {
      primary: "bg-indigo-600 text-white shadow-xl shadow-indigo-100 hover:shadow-2xl",
      secondary: "bg-white text-indigo-900 shadow-xl hover:shadow-2xl",
    };

    return (
      <motion.button
        onClick={onClick}
        className={`${baseClasses} ${variants[variant]} ${className}`}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        transition={{ type: "spring", stiffness: 400, damping: 17 }}
      >
        <motion.span
          className="absolute inset-0 bg-white/20 translate-x-[-100%]"
          whileHover={{ translateX: ['-100%', '100%'] }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
        />
        <span className="relative z-10 px-10 py-5 flex items-center gap-3">
          {children}
        </span>
      </motion.button>
    );
  };

  const NavLink = ({ href, children }) => (
    <motion.a
      href={href}
      className="relative text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors pb-1"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {children}
      <motion.span
        className="absolute bottom-0 left-0 w-full h-0.5 bg-indigo-600 origin-left"
        initial={{ scaleX: 0 }}
        whileHover={{ scaleX: 1 }}
        transition={{ duration: 0.3 }}
      />
    </motion.a>
  );

  return (
    <div className="min-h-screen flex flex-col font-sans bg-slate-50 text-slate-900">
      {/* Navbar - Fixed Shield Icon */}
      <header className="h-20 bg-white/90 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-8 shrink-0 fixed top-0 left-0 right-0 z-50 shadow-sm">
        <div className="flex items-center gap-3">
          {/* Custom clean logo container - no blurry outer shadow */}
          <div className="w-11 h-11 bg-indigo-600 rounded-2xl flex items-center justify-center text-white 
                          shadow-lg shadow-indigo-600/30 ring-4 ring-indigo-600/10">
            <ShieldCheck size={26} strokeWidth={2.5} />
          </div>
          <span className="font-extrabold text-2xl tracking-tight text-slate-900">Memora</span>
        </div>
        <div className="flex items-center gap-8">
          <nav className="hidden md:flex gap-8">
            <NavLink href="#features">Features</NavLink>
            <NavLink href="#how-to-join">How to Join</NavLink>
            <NavLink href="#about">About Us</NavLink>
            <NavLink href="#vision">Vision</NavLink>
            <motion.div
              onClick={() => navigate('/signin')}
              className="relative text-sm font-bold text-slate-500 hover:text-indigo-600 transition-colors pb-1 cursor-pointer"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Sign In
              <motion.span
                className="absolute bottom-0 left-0 w-full h-0.5 bg-indigo-600 origin-left"
                initial={{ scaleX: 0 }}
                whileHover={{ scaleX: 1 }}
                transition={{ duration: 0.3 }}
              />
            </motion.div>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative flex items-center justify-center py-32 overflow-hidden mt-20">
        <motion.div
          style={{ opacity: heroOpacity, scale: heroScale }}
          className="absolute inset-0 bg-gradient-to-br from-slate-900 via-indigo-900/90 to-slate-900"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
        <div className="relative z-10 text-center px-8 max-w-4xl">
          <FadeInSection>
            <h1 className="text-6xl font-black tracking-tight leading-tight mb-8 text-white">
              Control Your AI Context
            </h1>
          </FadeInSection>
          <FadeInSection delay={0.2}>
            <p className="text-xl text-indigo-100 font-medium mb-12 max-w-2xl mx-auto">
              Memora is your centralized hub for managing user context across multiple AI platforms. Maintain consistent, evolving personalization while protecting your privacy.
            </p>
          </FadeInSection>
          <FadeInSection delay={0.4}>
            <div className="flex justify-center gap-4">
              <AnimatedButton onClick={handleGetStarted} variant="secondary" className="text-lg">
                Get Started <ArrowRight size={24} strokeWidth={3} />
              </AnimatedButton>
              <AnimatedButton 
                onClick={() => navigate('/demo')} 
                variant="primary" 
                className="text-lg bg-white/10 backdrop-blur-sm border-2 border-white/30 hover:bg-white/20"
              >
                Try Demo <ExternalLink size={20} />
              </AnimatedButton>
            </div>
          </FadeInSection>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-8">
          <FadeInSection>
            <h2 className="text-4xl font-black text-slate-900 mb-12 text-center">
              Key Features
            </h2>
          </FadeInSection>
          <StaggerContainer>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                { icon: BrainCircuit, title: 'Behavior Analysis', desc: 'Autonomously track and adapt to your evolving preferences and behaviors.' },
                { icon: Lock, title: 'Privacy Protection', desc: 'Filter sensitive data and maintain secure, isolated contexts.' },
                { icon: Database, title: 'Cross-Platform Sync', desc: 'Consistent personalization across all your AI tools and sessions.' },
                { icon: Wifi, title: 'Session Management', desc: 'Isolate sessions while sharing global traits for seamless multi-tasking.' },
                { icon: Sparkles, title: 'Expertise Evaluation', desc: 'Automatically assess and update your skill levels in various domains.' },
                { icon: Zap, title: 'Prompt Enrichment', desc: 'Enhance AI prompts with personalized context for better responses.' },
              ].map((feature, i) => (
                <StaggerItem key={i}>
                  <motion.div
                    whileHover={{ y: -12, scale: 1.03 }}
                    transition={{ type: "spring", stiffness: 300 }}
                    className="group bg-white p-8 rounded-3xl border border-slate-200 shadow-sm hover:shadow-2xl transition-all duration-500"
                  >
                    <motion.div
                      className="w-14 h-14 bg-indigo-50 rounded-2xl flex items-center justify-center text-indigo-600 mb-6"
                      whileHover={{ scale: 1.2, rotate: 10 }}
                    >
                      <feature.icon size={28} strokeWidth={2.5} />
                    </motion.div>
                    <h3 className="text-xl font-black text-slate-900 mb-4">{feature.title}</h3>
                    <p className="text-slate-500 font-medium">{feature.desc}</p>
                  </motion.div>
                </StaggerItem>
              ))}
            </div>
          </StaggerContainer>
        </div>
      </section>

      {/* How to Join Section */}
      <section id="how-to-join" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-8">
          <FadeInSection>
            <h2 className="text-4xl font-black text-slate-900 mb-12 text-center">How to Join</h2>
          </FadeInSection>
          <StaggerContainer>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                { step: 1, title: 'Sign Up', desc: 'Create an account with your email or social login.' },
                { step: 2, title: 'Set Up Profile', desc: 'Complete a quick onboarding to define your initial preferences.' },
                { step: 3, title: 'Connect AIs', desc: 'Integrate with your favorite LLM tools and start interacting.' },
              ].map((step, i) => (
                <StaggerItem key={i}>
                  <motion.div
                    whileHover={{ scale: 1.08 }}
                    transition={{ type: "spring", stiffness: 400 }}
                    className="flex flex-col items-center text-center p-8 bg-slate-50 rounded-3xl border border-slate-200"
                  >
                    <motion.div
                      whileHover={{ rotate: 360, scale: 1.2 }}
                      transition={{ duration: 0.8, type: "spring" }}
                      className="w-20 h-20 bg-indigo-600 text-white rounded-full flex items-center justify-center text-3xl font-black mb-8 shadow-xl"
                    >
                      {step.step}
                    </motion.div>
                    <h3 className="text-2xl font-black text-slate-900 mb-4">{step.title}</h3>
                    <p className="text-slate-500 font-medium text-lg">{step.desc}</p>
                  </motion.div>
                </StaggerItem>
              ))}
            </div>
          </StaggerContainer>
          <FadeInSection delay={0.3}>
            <div className="flex justify-center mt-16">
              <AnimatedButton onClick={handleGetStarted} variant="primary" className="text-lg">
                Join Now <ChevronRight size={24} strokeWidth={3} />
              </AnimatedButton>
            </div>
          </FadeInSection>
        </div>
      </section>

      {/* About Us Section */}
      <section id="about" className="py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-8">
          <FadeInSection>
            <h2 className="text-4xl font-black text-slate-900 mb-12 text-center">About Us</h2>
          </FadeInSection>
          <FadeInSection delay={0.2}>
            <div className="max-w-3xl mx-auto text-center">
              <p className="text-xl text-slate-600 font-medium mb-12">
                Memora is built by a team of AI enthusiasts dedicated to bridging the gap between users and multiple AI systems. We believe in creating seamless, secure, and personalized AI experiences.
              </p>
              <motion.div className="flex justify-center gap-12">
                <motion.div whileHover={{ scale: 1.3, rotate: 15 }} transition={{ type: "spring" }}>
                  <Users size={56} className="text-indigo-600" />
                </motion.div>
                <motion.div whileHover={{ scale: 1.3, rotate: -15 }} transition={{ type: "spring" }}>
                  <Globe size={56} className="text-indigo-600" />
                </motion.div>
                <motion.div whileHover={{ scale: 1.3, rotate: 15 }} transition={{ type: "spring" }}>
                  <ExternalLink size={56} className="text-indigo-600" />
                </motion.div>
              </motion.div>
            </div>
          </FadeInSection>
        </div>
      </section>

      {/* Vision Section */}
      <section id="vision" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-8">
          <FadeInSection>
            <h2 className="text-4xl font-black text-slate-900 mb-12 text-center">Our Vision</h2>
          </FadeInSection>
          <FadeInSection delay={0.2}>
            <div className="max-w-3xl mx-auto text-center">
              <p className="text-xl text-slate-600 font-medium mb-12">
                To create a world where AI understands you deeply and consistently across all platforms, evolving with you while prioritizing your privacy and control.
              </p>
            </div>
          </FadeInSection>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-slate-900 text-slate-300 text-center">
        <p className="text-sm">© 2005-2025 Memora Inc. • <a href="#" className="hover:text-white transition">Contact Us</a> • <a href="#" className="hover:text-white transition">Privacy Policy</a></p>
      </footer>
    </div>
  );
};

export default LandingPage;